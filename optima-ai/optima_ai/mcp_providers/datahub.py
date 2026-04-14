"""Datahub MCP provider — fetches data catalog metadata for context-aware assistance."""

from __future__ import annotations

from typing import Any

import httpx

from optima_ai.mcp_providers.base import MCPContext, MCPProvider, MCPProviderRegistry


@MCPProviderRegistry.register
class DatahubProvider(MCPProvider):
    name = "datahub"

    GRAPHQL_ENDPOINT = "/api/graphql"

    async def _do_connect(self) -> None:
        self.base_url = self.config.get("base_url", "http://localhost:8080").rstrip("/")
        self.token = self.config.get("token", "")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.token}" if self.token else "",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    async def _do_disconnect(self) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_context(self, query: str, **kwargs: Any) -> list[MCPContext]:
        if query.startswith("dataset:"):
            return await self._fetch_dataset(query.split(":", 1)[1].strip())
        elif query.startswith("search:"):
            return await self._search_entities(query.split(":", 1)[1].strip())
        elif query.startswith("lineage:"):
            return await self._fetch_lineage(query.split(":", 1)[1].strip())
        else:
            return await self._search_entities(query)

    async def list_resources(self) -> list[dict[str, Any]]:
        gql = {
            "query": """
            query {
                search(input: {type: DATASET, query: "*", start: 0, count: 20}) {
                    searchResults { entity { urn type } }
                }
            }
            """
        }
        try:
            resp = await self._client.post(self.GRAPHQL_ENDPOINT, json=gql)
            if resp.status_code != 200:
                return []
            data = resp.json().get("data", {}).get("search", {}).get("searchResults", [])
            return [{"urn": r["entity"]["urn"], "type": r["entity"]["type"]} for r in data]
        except Exception:
            return []

    async def _fetch_dataset(self, urn: str) -> list[MCPContext]:
        gql = {
            "query": """
            query getDataset($urn: String!) {
                dataset(urn: $urn) {
                    urn name platform { name }
                    properties { description }
                    schemaMetadata {
                        fields { fieldPath nativeDataType description }
                    }
                    ownership {
                        owners { owner { ... on CorpUser { username } } }
                    }
                }
            }
            """,
            "variables": {"urn": urn},
        }
        resp = await self._client.post(self.GRAPHQL_ENDPOINT, json=gql)
        if resp.status_code != 200:
            return self._error(f"Failed to fetch dataset: {urn}")

        ds = resp.json().get("data", {}).get("dataset")
        if not ds:
            return self._error(f"Dataset not found: {urn}")

        fields = ds.get("schemaMetadata", {}).get("fields", [])
        field_text = "\n".join(
            f"  - {f['fieldPath']}: {f['nativeDataType']} — {f.get('description', '')}"
            for f in fields
        )
        owners = [
            o.get("owner", {}).get("username", "unknown")
            for o in ds.get("ownership", {}).get("owners", [])
        ]

        content = (
            f"Dataset: {ds['name']}\n"
            f"Platform: {ds.get('platform', {}).get('name', 'N/A')}\n"
            f"Owners: {', '.join(owners) if owners else 'N/A'}\n"
            f"Description: {ds.get('properties', {}).get('description', 'N/A')}\n\n"
            f"Schema:\n{field_text}"
        )
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="dataset",
                content=content,
                metadata={"urn": urn, "field_count": len(fields)},
            )
        ]

    async def _search_entities(self, search_query: str) -> list[MCPContext]:
        gql = {
            "query": """
            query searchDatasets($query: String!) {
                search(input: {type: DATASET, query: $query, start: 0, count: 10}) {
                    total
                    searchResults {
                        entity {
                            urn type
                            ... on Dataset { name platform { name } properties { description } }
                        }
                    }
                }
            }
            """,
            "variables": {"query": search_query},
        }
        resp = await self._client.post(self.GRAPHQL_ENDPOINT, json=gql)
        if resp.status_code != 200:
            return self._error(f"Datahub search failed: {resp.status_code}")

        data = resp.json().get("data", {}).get("search", {})
        results = data.get("searchResults", [])
        lines = [
            f"- {r['entity'].get('name', r['entity']['urn'])} "
            f"({r['entity'].get('platform', {}).get('name', 'N/A')})"
            for r in results
        ]
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="search_results",
                content=f"Datahub search results for '{search_query}' ({data.get('total', 0)} total):\n"
                + "\n".join(lines),
                metadata={"query": search_query, "total": data.get("total", 0)},
            )
        ]

    async def _fetch_lineage(self, urn: str) -> list[MCPContext]:
        gql = {
            "query": """
            query getLineage($urn: String!) {
                dataset(urn: $urn) {
                    urn name
                    upstream: lineage(input: {direction: UPSTREAM, start: 0, count: 10}) {
                        total
                        relationships { entity { urn type ... on Dataset { name } } }
                    }
                    downstream: lineage(input: {direction: DOWNSTREAM, start: 0, count: 10}) {
                        total
                        relationships { entity { urn type ... on Dataset { name } } }
                    }
                }
            }
            """,
            "variables": {"urn": urn},
        }
        resp = await self._client.post(self.GRAPHQL_ENDPOINT, json=gql)
        if resp.status_code != 200:
            return self._error(f"Lineage query failed for {urn}")

        ds = resp.json().get("data", {}).get("dataset", {})
        up = ds.get("upstream", {}).get("relationships", [])
        down = ds.get("downstream", {}).get("relationships", [])
        up_text = "\n".join(f"  ← {r['entity'].get('name', r['entity']['urn'])}" for r in up)
        down_text = "\n".join(f"  → {r['entity'].get('name', r['entity']['urn'])}" for r in down)

        content = (
            f"Lineage for {ds.get('name', urn)}:\n\n"
            f"Upstream ({len(up)}):\n{up_text or '  (none)'}\n\n"
            f"Downstream ({len(down)}):\n{down_text or '  (none)'}"
        )
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="lineage",
                content=content,
                metadata={"urn": urn, "upstream_count": len(up), "downstream_count": len(down)},
            )
        ]

    def _error(self, msg: str) -> list[MCPContext]:
        return [MCPContext(provider_name=self.name, resource_type="error", content=msg)]
