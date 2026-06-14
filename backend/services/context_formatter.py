class ContextFormatter:
  
    @staticmethod
    def build_context(
        sources
    ):

        context_blocks = []

        for source in sources:

            context_blocks.append(
                f"""
SOURCE:
{source["citation"]}

CONTENT:
{source["content"]}
"""
            )

        return "\n".join(
            context_blocks
        )