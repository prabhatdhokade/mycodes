"""GitHub MCP provider — pulls PR context, issues, code search, and repo metadata."""

from __future__ import annotations

from typing import Any

import httpx

from optima_ai.mcp_providers.base import MCPContext, MCPProvider, MCPProviderRegistry


@MCPProviderRegistry.register
class GitHubProvider(MCPProvider):
    name = "github"

    API_BASE = "https://api.github.com"

    async def _do_connect(self) -> None:
        self.token = self.config.get("token", "")
        self.default_repo = self.config.get("repo", "")  # owner/repo
        self._client = httpx.AsyncClient(
            base_url=self.API_BASE,
            headers={
                "Authorization": f"Bearer {self.token}" if self.token else "",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=30.0,
        )

    async def _do_disconnect(self) -> None:
        if self._client:
            await self._client.aclose()

    async def fetch_context(self, query: str, **kwargs: Any) -> list[MCPContext]:
        repo = kwargs.get("repo", self.default_repo)
        if not repo:
            return [
                MCPContext(
                    provider_name=self.name,
                    resource_type="error",
                    content="No repository configured for GitHub provider",
                )
            ]

        if query.startswith("pr:"):
            return await self._fetch_pr(repo, query.split(":", 1)[1].strip())
        elif query.startswith("issue:"):
            return await self._fetch_issue(repo, query.split(":", 1)[1].strip())
        elif query.startswith("file:"):
            return await self._fetch_file(repo, query.split(":", 1)[1].strip())
        elif query.startswith("search:"):
            return await self._search_code(repo, query.split(":", 1)[1].strip())
        else:
            return await self._fetch_repo_overview(repo)

    async def list_resources(self) -> list[dict[str, Any]]:
        if not self.default_repo:
            return []
        resp = await self._client.get(f"/repos/{self.default_repo}")
        if resp.status_code != 200:
            return []
        data = resp.json()
        return [
            {
                "name": data["full_name"],
                "description": data.get("description", ""),
                "default_branch": data.get("default_branch", "main"),
                "language": data.get("language", ""),
                "stars": data.get("stargazers_count", 0),
            }
        ]

    async def _fetch_pr(self, repo: str, pr_number: str) -> list[MCPContext]:
        resp = await self._client.get(f"/repos/{repo}/pulls/{pr_number}")
        if resp.status_code != 200:
            return self._error(f"Failed to fetch PR #{pr_number}: {resp.status_code}")

        pr = resp.json()
        diff_resp = await self._client.get(
            f"/repos/{repo}/pulls/{pr_number}",
            headers={"Accept": "application/vnd.github.v3.diff"},
        )
        diff = diff_resp.text if diff_resp.status_code == 200 else "(diff unavailable)"

        content = (
            f"PR #{pr['number']}: {pr['title']}\n"
            f"State: {pr['state']} | Author: {pr['user']['login']}\n"
            f"Base: {pr['base']['ref']} ← Head: {pr['head']['ref']}\n\n"
            f"Description:\n{pr.get('body', '(no description)')}\n\n"
            f"Diff:\n{diff[:8000]}"
        )
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="pull_request",
                content=content,
                metadata={"pr_number": pr_number, "repo": repo},
            )
        ]

    async def _fetch_issue(self, repo: str, issue_number: str) -> list[MCPContext]:
        resp = await self._client.get(f"/repos/{repo}/issues/{issue_number}")
        if resp.status_code != 200:
            return self._error(f"Failed to fetch issue #{issue_number}")

        issue = resp.json()
        labels = ", ".join(l["name"] for l in issue.get("labels", []))
        content = (
            f"Issue #{issue['number']}: {issue['title']}\n"
            f"State: {issue['state']} | Labels: {labels}\n\n"
            f"{issue.get('body', '(no body)')}"
        )
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="issue",
                content=content,
                metadata={"issue_number": issue_number, "repo": repo},
            )
        ]

    async def _fetch_file(self, repo: str, path: str) -> list[MCPContext]:
        resp = await self._client.get(f"/repos/{repo}/contents/{path}")
        if resp.status_code != 200:
            return self._error(f"File not found: {path}")

        data = resp.json()
        import base64

        content = base64.b64decode(data.get("content", "")).decode(errors="replace")
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="file",
                content=content[:16000],
                metadata={"path": path, "repo": repo, "sha": data.get("sha", "")},
            )
        ]

    async def _search_code(self, repo: str, search_query: str) -> list[MCPContext]:
        resp = await self._client.get(
            "/search/code",
            params={"q": f"{search_query} repo:{repo}", "per_page": 10},
        )
        if resp.status_code != 200:
            return self._error(f"Code search failed: {resp.status_code}")

        items = resp.json().get("items", [])
        results = "\n".join(f"- {i['path']} (score: {i.get('score', 0):.1f})" for i in items)
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="search_results",
                content=f"Search results for '{search_query}' in {repo}:\n{results}",
                metadata={"query": search_query, "result_count": len(items)},
            )
        ]

    async def _fetch_repo_overview(self, repo: str) -> list[MCPContext]:
        resp = await self._client.get(f"/repos/{repo}")
        if resp.status_code != 200:
            return self._error(f"Repository not found: {repo}")

        data = resp.json()
        content = (
            f"Repository: {data['full_name']}\n"
            f"Description: {data.get('description', 'N/A')}\n"
            f"Language: {data.get('language', 'N/A')}\n"
            f"Default branch: {data.get('default_branch', 'main')}\n"
            f"Stars: {data.get('stargazers_count', 0)} | "
            f"Forks: {data.get('forks_count', 0)}"
        )
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="repo_overview",
                content=content,
                metadata={"repo": repo},
            )
        ]

    def _error(self, msg: str) -> list[MCPContext]:
        return [MCPContext(provider_name=self.name, resource_type="error", content=msg)]
