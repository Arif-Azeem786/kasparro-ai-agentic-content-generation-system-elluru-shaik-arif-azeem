import traceback, json
from pathlib import Path
OUT = Path('outputs')
latest = OUT / 'latest_run.json'
print('latest exists:', latest.exists())
lr = json.loads(latest.read_text(encoding='utf-8'))
run_id = lr.get('run_id')
print('run_id:', run_id)
faq_path = OUT / f'faq_{run_id}.json'
data = json.loads(faq_path.read_text(encoding='utf-8'))
print('faq items:', len(data.get('faq', [])))

print('\\n--- Try simple retrieval agent ---')
try:
    from src.agents.retrieval_agent_simple import RetrievalAgentSimple
    print('Imported RetrievalAgentSimple')
    agent = RetrievalAgentSimple()
    texts = [f"{it.get('q','')} {it.get('a','')}" for it in data.get('faq',[])]
    agent.build_index(texts)
    print('build_index OK')
    print('Query result:', agent.query('How to use the product?', top_k=3))
except Exception:
    traceback.print_exc()

print('\\n--- Try FAISS retrieval agent ---')
try:
    from src.agents.retrieval_agent import RetrievalAgent
    print('Imported FAISS RetrievalAgent')
    agent = RetrievalAgent()
    texts = [f"{it.get('q','')} {it.get('a','')}" for it in data.get('faq',[])]
    agent.build_index(texts)
    print('FAISS build_index OK')
    print('FAISS Query result:', agent.query('How to use the product?', top_k=3))
except Exception:
    traceback.print_exc()
