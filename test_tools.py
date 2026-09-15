from app.tools.search_documents import SearchDocumentsTool


tool = SearchDocumentsTool()

print("NAME:")
print(tool.name)

print("\nDEFINITION:")
print(tool.definition())

print("\nVALID EXECUTION:")
print(
    tool.execute(
        tool.validate_arguments(
            {
                "query": "nghỉ phép",
                "limit": 2,
            }
        )
    )
)

print("\nINVALID EXECUTION:")
print(
    tool.validate_arguments(
        {
            "query": "",
            "limit": 100,
        }
    )
)