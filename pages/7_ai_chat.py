import streamlit as st

from utils.styles import inject_css
from utils.ai_chat import ask_gemini, get_api_key, build_data_context

inject_css()
st.title("🤖 AI 데이터 대화")
st.caption("대시보드 데이터에 대해 Gemini AI에게 자유롭게 질문해 보세요.")

# ── API 키 점검 ─────────────────────────────────────────
if not get_api_key():
    st.error(
        "**Gemini API 키가 설정되지 않았습니다.**\n\n"
        "프로젝트 루트의 `.env` 파일을 열어 `GEMINI_API_KEY` 값을 입력한 뒤 "
        "앱을 다시 실행하세요.\n\n"
        "API 키 발급: https://aistudio.google.com/app/apikey"
    )
    st.stop()

# ── 사이드바: 예시 질문 & 초기화 ────────────────────────
with st.sidebar:
    st.markdown("### 💡 예시 질문")
    examples = [
        "어떤 플랫폼의 ROAS가 가장 높아?",
        "전환수가 가장 많은 연령대는?",
        "예산 소진율이 가장 높은 캠페인 상태는?",
        "자사와 경쟁사의 CTR을 비교해줘",
        "세션이 가장 많은 지역 TOP5는?",
        "소재유형 중 CTR이 가장 좋은 건 뭐야?",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["pending_question"] = ex

    st.markdown("---")
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.rerun()

# ── 대화 상태 초기화 ────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# ── 이전 대화 렌더링 ────────────────────────────────────
for msg in st.session_state["chat_messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 입력 처리 (직접 입력 또는 예시 버튼) ────────────────
prompt = st.chat_input("데이터에 대해 무엇이든 물어보세요...")
if not prompt and "pending_question" in st.session_state:
    prompt = st.session_state.pop("pending_question")

if prompt:
    # 사용자 메시지 표시 및 저장
    st.session_state["chat_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답
    with st.chat_message("assistant"):
        with st.spinner("데이터를 분석하는 중..."):
            try:
                # 현재 질문은 제외한 직전까지의 기록 전달
                history = st.session_state["chat_messages"][:-1]
                answer = ask_gemini(prompt, history)
            except Exception as e:
                answer = f"⚠️ 답변 생성 중 오류가 발생했습니다: {e}"
        st.markdown(answer)

    st.session_state["chat_messages"].append({"role": "assistant", "content": answer})
