# A tiny deterministic template engine that maps fields -> JSON structure
def render(template: dict, blocks: dict, product, qa_list: list) -> dict:
    # template is a dict that defines which blocks go where
    # Example: template = {"title": "{{product.name}}", "sections": ["benefits_block","ingredients_block"]}
    out = {}
    out["title"] = template.get("title", "").replace("{{product.name}}", product.name)
    out["meta"] = {"price_inr": product.price_inr}
    out["sections"] = []
    for sec in template.get("sections", []):
        out["sections"].append({ "id": sec, "content": blocks.get(sec) })
    if template.get("include_faq"):
        out["faq"] = qa_list
    return out
