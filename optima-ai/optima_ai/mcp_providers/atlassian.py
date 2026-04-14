"""Atlassian MCP provider — fetches Jira tickets and Confluence pages for context."""

from __future__ import annotations

from typing import Any

import httpx

from optima_ai.mcp_providers.base import MCPContext, MCPProvider, MCPProviderRegistry


@MCPProviderRegistry.register
class AtlassianProvider(MCPProvider):
    name = "atlassian"

    async def _do_connect(self) -> None:
        self.base_url = self.config.get("base_url", "").rstrip("/")
        self.email = self.config.get("email", "")
        self.api_token = self.config.get("api_token", "")
        self.project_key = self.config.get("project_key", "")

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            auth=(self.email, self.api_token) if self.email and self.api_token else None,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30.0,
        )

    async def _do_disconnect(self) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_context(self, query: str, **kwargs: Any) -> list[MCPContext]:
        if query.startswith("jira:"):
            return await self._fetch_jira_issue(query.split(":", 1)[1].strip())
        elif query.startswith("jql:"):
            return await self._search_jira(query.split(":", 1)[1].strip())
        elif query.startswith("confluence:"):
            return await self._fetch_confluence_page(query.split(":", 1)[1].strip())
        elif query.startswith("confluence-search:"):
            return await self._search_confluence(query.split(":", 1)[1].strip())
        else:
            return await self._search_jira(query)

    async def list_resources(self) -> list[dict[str, Any]]:
        try:
            resp = await self._client.get(
                "/rest/api/2/search",
                params={"jql": f"project = {self.project_key} ORDER BY updated DESC", "maxResults": 20},
            )
            if resp.status_code != 200:
                return []
            issues = resp.json().get("issues", [])
            return [
                {"key": i["key"], "summary": i["fields"]["summary"], "status": i["fields"]["status"]["name"]}
                for i in issues
            ]
        except Exception:
            return []

    async def _fetch_jira_issue(self, issue_key: str) -> list[MCPContext]:
        resp = await self._client.get(f"/rest/api/2/issue/{issue_key}")
        if resp.status_code != 200:
            return self._error(f"Jira issue {issue_key} not found")

        data = resp.json()
        fields = data["fields"]
        content = (
            f"Issue: {data['key']} — {fields['summary']}\n"
            f"Type: {fields['issuetype']['name']} | Status: {fields['status']['name']}\n"
            f"Priority: {fields.get('priority', {}).get('name', 'N/A')}\n"
            f"Assignee: {(fields.get('assignee') or {}).get('displayName', 'Unassigned')}\n\n"
            f"Description:\n{fields.get('description', '(no description)')}"
        )
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="jira_issue",
                content=content,
                metadata={"key": issue_key},
            )
        ]

    async def _search_jira(self, jql: str) -> list[MCPContext]:
        resp = await self._client.get(
            "/rest/api/2/search",
            params={"jql": jql, "maxResults": 10, "fields": "summary,status,assignee"},
        )
        if resp.status_code != 200:
            return self._error(f"JQL search failed: {resp.status_code}")

        issues = resp.json().get("issues", [])
        lines = [
            f"- {i['key']}: {i['fields']['summary']} [{i['fields']['status']['name']}]"
            for i in issues
        ]
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="jira_search",
                content=f"JQL results ({len(issues)} issues):\n" + "\n".join(lines),
                metadata={"jql": jql, "count": len(issues)},
            )
        ]

    async def _fetch_confluence_page(self, page_id: str) -> list[MCPContext]:
        resp = await self._client.get(
            f"/wiki/rest/api/content/{page_id}",
            params={"expand": "body.storage"},
        )
        if resp.status_code != 200:
            return self._error(f"Confluence page {page_id} not found")

        data = resp.json()
        body_html = data.get("body", {}).get("storage", {}).get("value", "")
        import re
        body_text = re.sub(r"<[^>]+>", "", body_html)

        return [
            MCPContext(
                provider_name=self.name,
                resource_type="confluence_page",
                content=f"Page: {data['title']}\n\n{body_text[:8000]}",
                metadata={"page_id": page_id, "title": data["title"]},
            )
        ]

    async def _search_confluence(self, cql: str) -> list[MCPContext]:
        resp = await self._client.get(
            "/wiki/rest/api/content/search",
            params={"cql": cql, "limit": 10},
        )
        if resp.status_code != 200:
            return self._error(f"Confluence search failed: {resp.status_code}")

        results = resp.json().get("results", [])
        lines = [f"- [{r['id']}] {r['title']}" for r in results]
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="confluence_search",
                content=f"Confluence results:\n" + "\n".join(lines),
                metadata={"cql": cql, "count": len(results)},
            )
        ]

    def _error(self, msg: str) -> list[MCPContext]:
        return [MCPContext(provider_name=self.name, resource_type="error", content=msg)]
