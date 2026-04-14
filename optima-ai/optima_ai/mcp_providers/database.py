"""Database MCP provider — queries schema metadata and sample data for context."""

from __future__ import annotations

from typing import Any

from optima_ai.mcp_providers.base import MCPContext, MCPProvider, MCPProviderRegistry


@MCPProviderRegistry.register
class DatabaseProvider(MCPProvider):
    name = "database"

    async def _do_connect(self) -> None:
        self.connection_url = self.config.get("connection_url", "")
        self.schema = self.config.get("schema", "public")
        self.max_rows_preview = self.config.get("max_rows_preview", 5)
        self._engine = None

        if self.connection_url:
            from sqlalchemy.ext.asyncio import create_async_engine

            self._engine = create_async_engine(
                self.connection_url,
                pool_size=2,
                max_overflow=3,
                pool_pre_ping=True,
            )

    async def _do_disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def fetch_context(self, query: str, **kwargs: Any) -> list[MCPContext]:
        """Fetch table schema or run a read-only introspection query."""
        if not self._engine:
            return [
                MCPContext(
                    provider_name=self.name,
                    resource_type="error",
                    content="Database provider not connected — no connection URL configured",
                )
            ]

        results: list[MCPContext] = []
        if query.startswith("schema:"):
            table_name = query.split(":", 1)[1].strip()
            results.extend(await self._fetch_table_schema(table_name))
        elif query.startswith("tables"):
            results.extend(await self._list_tables())
        else:
            results.extend(await self._fetch_table_schema(query))
        return results

    async def list_resources(self) -> list[dict[str, Any]]:
        if not self._engine:
            return []
        tables = await self._list_tables()
        return [{"table": ctx.metadata.get("table", ""), "type": "table"} for ctx in tables]

    async def _list_tables(self) -> list[MCPContext]:
        from sqlalchemy import text

        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = :schema ORDER BY table_name"
                ),
                {"schema": self.schema},
            )
            rows = result.fetchall()

        table_list = "\n".join(f"- {row[0]}" for row in rows)
        return [
            MCPContext(
                provider_name=self.name,
                resource_type="table_list",
                content=f"Tables in schema '{self.schema}':\n{table_list}",
                metadata={"schema": self.schema, "count": len(rows)},
            )
        ]

    async def _fetch_table_schema(self, table_name: str) -> list[MCPContext]:
        from sqlalchemy import text

        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT column_name, data_type, is_nullable, column_default "
                    "FROM information_schema.columns "
                    "WHERE table_schema = :schema AND table_name = :table "
                    "ORDER BY ordinal_position"
                ),
                {"schema": self.schema, "table": table_name},
            )
            columns = result.fetchall()

        if not columns:
            return [
                MCPContext(
                    provider_name=self.name,
                    resource_type="error",
                    content=f"Table '{table_name}' not found in schema '{self.schema}'",
                )
            ]

        schema_text = f"Table: {self.schema}.{table_name}\n"
        schema_text += "Columns:\n"
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            schema_text += f"  - {col[0]}: {col[1]} {nullable}{default}\n"

        return [
            MCPContext(
                provider_name=self.name,
                resource_type="table_schema",
                content=schema_text,
                metadata={"table": table_name, "column_count": len(columns)},
            )
        ]
