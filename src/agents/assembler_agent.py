from .base_agent import BaseAgent
from ..engine.template_engine import render
from typing import Dict

class AssemblerAgent(BaseAgent):
    def run(self, product, blocks, qa_list, comparison, templates) -> Dict:
        product_json = render(templates["product"], blocks, product, qa_list)
        faq_json = render(templates["faq"], blocks, product, qa_list)
        comparison_json = render(templates["comparison"], blocks, product, qa_list)
        # attach comparison details
        comparison_json["comparison"] = comparison
        return {"product_page": product_json, "faq": faq_json, "comparison_page": comparison_json}
