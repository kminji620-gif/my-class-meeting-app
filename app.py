import streamlit as st
import google.generativeai as genai
import random

# UI 설정 및 스타일 정의 (화자별 색상)
st.set_page_config(page_title="5학년 질문 회의 생성기", layout="centered")

# CSS 스타일 정의
st.markdown("""
<style>
    /* 색상 정의 */
    .moderator { color: #2E86C1; font-weight: bold; } /* 사회자: 파랑 */
    .student1 { color: #E74C3C; font-weight: bold; }   /* 학생1: 빨강 */
    .student2 { color: #27AE60; font-weight: bold; }   /* 학생2: 초록 */
    .student3 { color: #8E44AD; font-weight: bold; }   /* 학생3: 보라 */
    .student_gen { color: #A04000; font-weight: bold; }/* 나머지 학생: 갈색 */
    
    /* 질문 태그 스타일 */
    .tag_intent { background-color: #D6EAF8; color: #1B4F72; padding: 2px 5px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;}
    .tag_clarify { background-color: #D4EFDF; color: #145A32; padding: 2px 5px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;}
    .tag_alt { background-color: #FCF3CF; color: #7E5109; padding: 2px 5px; border-radius: 4px; font-size: 0.8em; margin-right: 5px;}
    
    /* 대본 박스 스타일 */
    .script-box {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        padding: 20px;
        border-radius: 10px;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_with_html=True)

# 1. API 키 설정 (보안 강화)
# Streamlit Secrets에서 키를 가져옵니다.
api_key = st.secrets.get("gemini_api_key")

# API 키가 설정되었는지 확인
if not api_key:
    st.error("⚠️ API 키가 설정되지 않았습니다. Streamlit Cloud Settings > Secrets에서 'gemini_api_key'를 입력해주세요.")
    st.stop() # 키가 없으면 여기서 실행 중단

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"⚠️ Gemini API 연결 중 오류가 발생했습니다: {e}")
    st.stop()

# 2. 추천 주제 리스트
RECOMMENDED_TOPICS = [
    "급식실 잔반을 줄이기 위한 우리 반 실천 방안",
    "현장체험학습 장소 결정하기 (박물관 vs 테마파크)",
    "복도 우측통행을 즐겁게 실천하는 방법",
    "학급 장기자랑의 종목과 순서 정하기",
    "스마트폰 사용 시간을 줄이는 우리만의 약속",
    "쉬는 시간 교실 놀이 기구 사용 규칙"
]

# 3. UI 구성 (메인 화면)
st.title("🏫 5학년 질문 회의 대본 생성기")
st.write("상대의 말을 듣고 질문하며 해결책을 찾아가는 민주적 회의 연습 도구입니다.")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    if st.button("💡 주제 추천받기"):
        st.session_state.topic_input = random.choice(RECOMMENDED_TOPICS)
    
    topic = st.text_input("회의 주제", 
                         value=st.session_state.get('topic_input', ''),
                         placeholder="주제를 입력하세요.")
    
    count = st.slider("참여 인원 (사회자 포함)", 3, 24, 4)
    st.info("3~6명은 모둠용, 7~24명은 학급 전체용 대본으로 생성됩니다.")

# 화자별 CSS 클래스를 매핑하는 함수
def get_speaker_class(speaker_name):
    if "사회자" in speaker_name: return "moderator"
    elif "학생 1" in speaker_name: return "student1"
    elif "학생 2" in speaker_name: return "student2"
    elif "학생 3" in speaker_name: return "student3"
    else: return "student_gen"

# 질문 태그를 HTML로 변환하는 함수
def format_tags(text):
    text = text.replace("[의도 파악]", '<span class="tag_intent">💬 의도 파악</span>')
    text = text.replace("[의미 명료화]", '<span class="tag_clarify">❓ 의미 명료화</span>')
    text = text.replace("[대안 탐색]", '<span class="tag_alt">💡 대안 탐색</span>')
    return text

# 대본의 텍스트를 색상형 HTML로 변환하는 함수
def colorize_script(raw_script):
    colored_lines = []
    lines = raw_script.split('\n')
    
    for line in lines:
        if ':' in line:
            speaker, dialogue = line.split(':', 1)
            speaker = speaker.strip()
            speaker_class = get_speaker_class(speaker)
            formatted_dialogue = format_tags(dialogue.strip())
            
            # HTML 구조로 변경
            colored_line = f'<div><span class="{speaker_class}">{speaker}:</span> {formatted_dialogue}</div>'
            colored_lines.append(colored_line)
        elif line.strip(): # 빈 줄이 아닌 경우
            colored_lines.append(f'<div>{format_tags(line.strip())}</div>')
        else: # 빈 줄
            colored_lines.append('<br>')
            
    return '<div class="script-box">' + ''.join(colored_lines) + '</div>'

# 4. 대본 생성 로직
if st.button("🚀 대본 생성하기", use_container_width=True):
    if not topic:
        st.warning("먼저 주제를 입력하거나 추천을 받아보세요!")
    else:
        with st.spinner("5학년 수준의 맞춤형 대본을 작성 중입니다..."):
            prompt = f"""
            너는 초등학교 5학년 수준의 회의 대본을 작성하는 전문가야.
            아래 조건에 맞춰서 자연스러운 구어체 대본을 써줘.

            [조건]
            1. 주제: {topic}
            2. 인원: {count}명 (각자 이름은 '사회자', '학생 1', '학생 2', ..., '학생 {count-1}'로 표시)
            3. 문체: 학생들끼리 서로 존댓말(경어체)을 사용하며 존중하는 분위기.
            4. 필수 포함 사항:
               - 단순히 의견만 말하는 게 아니라, 반드시 앞 사람의 말을 '경청'하고 있음을 나타내는 반응을 넣을 것.
               - 다음 3가지 질문 유형이 대본 전반에 골고루, 많이 포함되도록 할 것:
                 ① 발화자의 의도를 파악하기 위한 질문 (예: "~라는 마음으로 하신 말씀인가요?")
                 ② 의미를 명료하게 하기 위한 질문 (예: "~라는 게 정확히 어떤 뜻인지 알려줄 수 있나요?")
                 ③ 대안이나 정보를 찾기 위한 질문 (예: "만약 ~한다면 어떻게 하면 좋을까요?")
            5. 대본 중간에 해당 질문이 어떤 유형인지 반드시 대사 직전에 [의도 파악], [의미 명료화], [대안 탐색]이라고 표시해줘.
               예) 학생 2: [의도 파악] 학생 1님의 의견 잘 들었습니다. 혹시...
            6. 마지막은 사회자가 의견을 정리하며 훈훈하게 마무리할 것.
            
            대본만 출력해줘.
            """
            
            try:
                response = model.generate_content(prompt)
                
                # 생성된 대본에 색상 입히기
                colored_script_html = colorize_script(response.text)
                
                st.markdown("---")
                # HTML로 출력
                st.markdown(colored_script_html, unsafe_allow_with_html=True)
                
                # 다운로드 버튼 제공 (색상 없는 순수 텍스트)
                st.download_button("📂 대본 파일로 저장하기", response.text, file_name=f"회의대본_{topic}.txt")
                
            except Exception as e:
                st.error(f"대본 생성 중 오류가 발생했습니다: {e}")
