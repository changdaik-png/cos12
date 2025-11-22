import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import os
from typing import Optional

# OpenAI API (선택적)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="초등학교 상담기록부",
    page_icon="📚",
    layout="wide"
)

# OpenAI 클라이언트 초기화 (선택적)
@st.cache_resource
def init_openai():
    """OpenAI 클라이언트 초기화"""
    if not OPENAI_AVAILABLE:
        return None
    
    # 환경 변수 우선 확인
    api_key = os.getenv("OPENAI_API_KEY", "")
    
    # 환경 변수가 없으면 Streamlit secrets에서 확인
    if not api_key:
        try:
            if "OPENAI_API_KEY" in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, AttributeError, FileNotFoundError):
            pass
    
    if not api_key:
        return None
    
    try:
        return OpenAI(api_key=api_key)
    except Exception:
        return None

# AI 텍스트 개선 함수
def improve_text_with_ai(client, text: str) -> Optional[str]:
    """ChatGPT API를 사용하여 텍스트를 더 정교하게 개선"""
    if not client or not text.strip():
        return None
    
    try:
        prompt = f"""초등학교 상담 기록의 상담 내용을 더 정교하고 상세하게 작성해주세요.
다음은 간단히 작성된 상담 내용입니다:
"{text}"

요구사항:
- 상담 내용을 더 구체적이고 상세하게 작성
- 전문적이면서도 이해하기 쉬운 문장으로 표현
- 초등학교 상담 기록에 적합한 톤으로 작성
- 원본 내용의 핵심은 유지하면서 더 풍부하게 설명
- 2-3문단 정도의 적절한 분량으로 작성

개선된 상담 내용:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 또는 "gpt-3.5-turbo" 사용 가능
            messages=[
                {"role": "system", "content": "당신은 초등학교 상담 기록을 전문적으로 작성하는 교육 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        improved_text = response.choices[0].message.content.strip()
        return improved_text
    except Exception as e:
        st.error(f"AI 개선 중 오류 발생: {str(e)}")
        return None

# Supabase 클라이언트 초기화
@st.cache_resource
def init_supabase():
    """Supabase 클라이언트 초기화"""
    # 환경 변수를 우선적으로 확인 (서버 환경에 적합)
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    
    # 환경 변수가 없으면 Streamlit secrets에서 확인
    if not url or not key:
        try:
            if "SUPABASE_URL" in st.secrets:
                url = st.secrets["SUPABASE_URL"] if not url else url
            if "SUPABASE_KEY" in st.secrets:
                key = st.secrets["SUPABASE_KEY"] if not key else key
        except (KeyError, AttributeError, FileNotFoundError):
            pass
    
    if not url or not key:
        st.error("⚠️ Supabase 설정이 필요합니다. 환경 변수 또는 Streamlit secrets에 SUPABASE_URL과 SUPABASE_KEY를 설정해주세요.")
        st.stop()
    
    return create_client(url, key)

# 비밀번호 확인
def check_password():
    """비밀번호 확인 함수"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 초등학교 상담기록부 로그인")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 비밀번호를 입력하세요")
            password = st.text_input("비밀번호", type="password", key="password_input")
            
            # 기본 비밀번호 읽기 (서버 환경 고려)
            # 우선순위: 환경 변수 > Streamlit secrets > 기본값
            default_password = "1234"  # 기본값
            
            try:
                # 1. 환경 변수에서 먼저 확인 (서버 환경에서 주로 사용)
                env_password = os.getenv("ADMIN_PASSWORD")
                if env_password:
                    default_password = env_password
                else:
                    # 2. Streamlit secrets에서 확인 (로컬 개발 환경)
                    try:
                        # Streamlit Cloud나 로컬 secrets에서 읽기
                        if "ADMIN_PASSWORD" in st.secrets:
                            default_password = st.secrets["ADMIN_PASSWORD"]
                        elif hasattr(st.secrets, "ADMIN_PASSWORD"):
                            default_password = st.secrets.ADMIN_PASSWORD
                    except (KeyError, AttributeError, FileNotFoundError):
                        # secrets 파일이 없어도 계속 진행
                        pass
            except Exception as e:
                # 모든 방법 실패 시 기본값 사용
                pass
            
            if st.button("로그인", type="primary", use_container_width=True):
                # 입력한 비밀번호와 저장된 비밀번호 비교 (문자열 비교)
                if str(password) == str(default_password):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ 비밀번호가 올바르지 않습니다.")
        
        st.stop()
    
    return True

# 메인 애플리케이션
def main():
    """메인 애플리케이션"""
    st.title("📚 초등학교 상담기록부")
    st.markdown("---")
    
    supabase = init_supabase()
    
    # 사이드바 - 메뉴
    with st.sidebar:
        st.header("메뉴")
        menu = st.radio(
            "선택하세요",
            ["📝 상담기록 작성", "📋 상담기록 조회", "✏️ 상담기록 수정", "🗑️ 상담기록 삭제"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # 상담기록 작성
    if menu == "📝 상담기록 작성":
        st.header("📝 상담기록 작성")
        
        # OpenAI 클라이언트 초기화
        openai_client = init_openai()
        if openai_client:
            st.info("✨ AI 개선 기능이 활성화되었습니다!")
        else:
            st.warning("⚠️ AI 기능을 사용하려면 OPENAI_API_KEY를 설정해주세요. (secrets 또는 환경 변수)")
        
        # AI 개선 버튼 (form 밖)
        if openai_client:
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                temp_content = st.text_area(
                    "📝 상담 내용을 입력하고 AI로 개선해보세요",
                    value=st.session_state.get('temp_consult_content', ''),
                    height=100,
                    placeholder="간단한 상담 내용을 입력하세요.\n예: 학생이 수업 중 집중력이 부족하고 산만함",
                    key="temp_content_for_ai"
                )
                st.session_state.temp_consult_content = temp_content
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)  # 정렬을 위한 공간
                if st.button("✨ AI로 개선하기", use_container_width=True, type="secondary"):
                    if temp_content.strip():
                        with st.spinner("🤖 AI가 상담 내용을 개선하고 있습니다... 잠시만 기다려주세요."):
                            improved_text = improve_text_with_ai(openai_client, temp_content)
                            if improved_text:
                                st.session_state.improved_consult_content = improved_text
                                st.session_state.show_improved = True
                                st.session_state.temp_consult_content = improved_text  # 개선된 내용으로 업데이트
                                st.success("✅ AI 개선이 완료되었습니다!")
                                st.rerun()
                            else:
                                st.error("❌ AI 개선 중 오류가 발생했습니다.")
                    else:
                        st.warning("⚠️ 상담 내용을 먼저 입력해주세요.")
            st.markdown("---")
        
        # AI 개선된 내용 표시
        if 'show_improved' in st.session_state and st.session_state.show_improved and 'improved_consult_content' in st.session_state:
            st.markdown("---")
            st.markdown("### ✨ AI 개선된 상담 내용")
            st.text_area(
                "개선된 내용",
                value=st.session_state.improved_consult_content,
                height=150,
                key="improved_content_display",
                disabled=True
            )
            col_use, col_ignore = st.columns(2)
            with col_use:
                if st.button("✅ 이 내용 사용하기", use_container_width=True, key="use_improved"):
                    st.session_state.consult_content_to_use = st.session_state.improved_consult_content
                    st.session_state.show_improved = False
                    del st.session_state.improved_consult_content
                    st.rerun()
            with col_ignore:
                if st.button("❌ 무시하기", use_container_width=True, key="ignore_improved"):
                    st.session_state.show_improved = False
                    if 'improved_consult_content' in st.session_state:
                        del st.session_state.improved_consult_content
                    st.rerun()
            st.markdown("---")
        
        with st.form("상담기록 작성 폼", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                student_name = st.text_input("학생 이름 *", placeholder="홍길동")
                grade = st.number_input("학년 *", min_value=1, max_value=6, value=1)
                class_num = st.number_input("반 *", min_value=1, max_value=20, value=1)
                counselor = st.text_input("상담자 (교사 이름) *", placeholder="김선생")
            
            with col2:
                consult_date = st.date_input("상담 일자 *", value=datetime.now().date())
                
                # 상담 내용 입력 (AI 개선된 내용이 있으면 사용)
                initial_content = st.session_state.get('consult_content_to_use', '')
                if 'consult_content_to_use' in st.session_state:
                    del st.session_state.consult_content_to_use
                
                consult_content = st.text_area(
                    "상담 내용 *", 
                    height=150, 
                    value=initial_content,
                    placeholder="상담 내용을 간단히 입력하세요.\n예: 학생이 수업 중 집중력이 부족함",
                    key="consult_content_input"
                )
                
                # AI 개선 버튼 (form 외부에서 처리)
                notes = st.text_area("비고", height=100, placeholder="추가 메모사항이 있으면 입력하세요...")
            
            submitted = st.form_submit_button("💾 저장하기", type="primary", use_container_width=True)
            
            if submitted:
                if not all([student_name, counselor, consult_content]):
                    st.error("❌ 필수 항목(*)을 모두 입력해주세요.")
                else:
                    try:
                        data = {
                            "student_name": student_name,
                            "grade": grade,
                            "class_num": class_num,
                            "consult_date": consult_date.isoformat(),
                            "consult_content": consult_content,
                            "counselor": counselor,
                            "notes": notes if notes else None,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        result = supabase.table("counseling_records").insert(data).execute()
                        
                        if result.data:
                            st.success(f"✅ 상담기록이 성공적으로 저장되었습니다!")
                            st.balloons()
                        else:
                            st.error("❌ 저장 중 오류가 발생했습니다.")
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
    
    # 상담기록 조회
    elif menu == "📋 상담기록 조회":
        st.header("📋 상담기록 조회")
        
        # 검색 필터
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("학생 이름으로 검색", placeholder="이름 입력")
        with col2:
            search_grade = st.selectbox("학년으로 필터", ["전체"] + [str(i) for i in range(1, 7)])
        with col3:
            search_class = st.selectbox("반으로 필터", ["전체"] + [str(i) for i in range(1, 21)])
        
        try:
            query = supabase.table("counseling_records").select("*")
            
            # 필터 적용
            if search_name:
                query = query.ilike("student_name", f"%{search_name}%")
            if search_grade != "전체":
                query = query.eq("grade", int(search_grade))
            if search_class != "전체":
                query = query.eq("class_num", int(search_class))
            
            # 최신순 정렬
            query = query.order("consult_date", desc=True)
            
            result = query.execute()
            
            if result.data:
                st.info(f"📊 총 {len(result.data)}개의 상담기록이 있습니다.")
                
                for idx, record in enumerate(result.data, 1):
                    with st.expander(f"📌 {record.get('student_name', 'N/A')} - {record.get('grade', 'N/A')}학년 {record.get('class_num', 'N/A')}반 ({record.get('consult_date', 'N/A')})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**학생 이름:** {record.get('student_name', 'N/A')}")
                            st.write(f"**학년/반:** {record.get('grade', 'N/A')}학년 {record.get('class_num', 'N/A')}반")
                            st.write(f"**상담 일자:** {record.get('consult_date', 'N/A')}")
                        with col2:
                            st.write(f"**상담자:** {record.get('counselor', 'N/A')}")
                            st.write(f"**작성일시:** {record.get('created_at', 'N/A')[:19] if record.get('created_at') else 'N/A'}")
                        
                        st.markdown("---")
                        st.write(f"**상담 내용:**")
                        st.write(record.get('consult_content', 'N/A'))
                        
                        if record.get('notes'):
                            st.write(f"**비고:**")
                            st.write(record.get('notes'))
            else:
                st.info("📭 검색 결과가 없습니다.")
                
        except Exception as e:
            st.error(f"❌ 조회 중 오류 발생: {str(e)}")
            st.info("💡 데이터베이스 테이블이 생성되지 않았을 수 있습니다. Supabase에서 'counseling_records' 테이블을 생성해주세요.")
    
    # 상담기록 수정
    elif menu == "✏️ 상담기록 수정":
        st.header("✏️ 상담기록 수정")
        
        try:
            # 모든 기록 가져오기
            result = supabase.table("counseling_records").select("*").order("consult_date", desc=True).execute()
            
            if not result.data:
                st.info("📭 수정할 상담기록이 없습니다.")
            else:
                # 수정할 기록 선택
                record_options = {
                    f"{r.get('student_name', 'N/A')} - {r.get('grade', 'N/A')}학년 {r.get('class_num', 'N/A')}반 ({r.get('consult_date', 'N/A')})": r
                    for r in result.data
                }
                
                selected_key = st.selectbox("수정할 상담기록을 선택하세요", list(record_options.keys()))
                selected_record = record_options[selected_key]
                
                st.markdown("---")
                
                with st.form("상담기록 수정 폼"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        student_name = st.text_input("학생 이름 *", value=selected_record.get('student_name', ''))
                        grade = st.number_input("학년 *", min_value=1, max_value=6, value=selected_record.get('grade', 1))
                        class_num = st.number_input("반 *", min_value=1, max_value=20, value=selected_record.get('class_num', 1))
                        counselor = st.text_input("상담자 (교사 이름) *", value=selected_record.get('counselor', ''))
                    
                    with col2:
                        consult_date = st.date_input(
                            "상담 일자 *",
                            value=datetime.fromisoformat(selected_record.get('consult_date', datetime.now().isoformat())).date()
                        )
                        consult_content = st.text_area(
                            "상담 내용 *",
                            value=selected_record.get('consult_content', ''),
                            height=150
                        )
                        notes = st.text_area(
                            "비고",
                            value=selected_record.get('notes', '') or '',
                            height=100
                        )
                    
                    submitted = st.form_submit_button("수정하기", type="primary", use_container_width=True)
                    
                    if submitted:
                        if not all([student_name, counselor, consult_content]):
                            st.error("❌ 필수 항목(*)을 모두 입력해주세요.")
                        else:
                            try:
                                update_data = {
                                    "student_name": student_name,
                                    "grade": grade,
                                    "class_num": class_num,
                                    "consult_date": consult_date.isoformat(),
                                    "consult_content": consult_content,
                                    "counselor": counselor,
                                    "notes": notes if notes else None
                                }
                                
                                result = supabase.table("counseling_records").update(update_data).eq("id", selected_record.get('id')).execute()
                                
                                if result.data:
                                    st.success("✅ 상담기록이 성공적으로 수정되었습니다!")
                                    st.rerun()
                                else:
                                    st.error("❌ 수정 중 오류가 발생했습니다.")
                            except Exception as e:
                                st.error(f"❌ 오류 발생: {str(e)}")
                                
        except Exception as e:
            st.error(f"❌ 조회 중 오류 발생: {str(e)}")
    
    # 상담기록 삭제
    elif menu == "🗑️ 상담기록 삭제":
        st.header("🗑️ 상담기록 삭제")
        st.warning("⚠️ 삭제된 상담기록은 복구할 수 없습니다.")
        
        try:
            # 모든 기록 가져오기
            result = supabase.table("counseling_records").select("*").order("consult_date", desc=True).execute()
            
            if not result.data:
                st.info("📭 삭제할 상담기록이 없습니다.")
            else:
                # 삭제할 기록 선택
                record_options = {
                    f"{r.get('student_name', 'N/A')} - {r.get('grade', 'N/A')}학년 {r.get('class_num', 'N/A')}반 ({r.get('consult_date', 'N/A')})": r
                    for r in result.data
                }
                
                selected_key = st.selectbox("삭제할 상담기록을 선택하세요", list(record_options.keys()))
                selected_record = record_options[selected_key]
                
                st.markdown("---")
                st.write("**선택한 상담기록:**")
                st.json(selected_record)
                
                if st.button("🗑️ 삭제하기", type="primary", use_container_width=True):
                    try:
                        result = supabase.table("counseling_records").delete().eq("id", selected_record.get('id')).execute()
                        
                        if result.data:
                            st.success("✅ 상담기록이 성공적으로 삭제되었습니다!")
                            st.rerun()
                        else:
                            st.error("❌ 삭제 중 오류가 발생했습니다.")
                    except Exception as e:
                        st.error(f"❌ 오류 발생: {str(e)}")
                        
        except Exception as e:
            st.error(f"❌ 조회 중 오류 발생: {str(e)}")

# 앱 실행
if __name__ == "__main__":
    if check_password():
        main()
