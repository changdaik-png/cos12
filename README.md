# 초등학교 상담기록부

Streamlit과 Supabase를 사용한 초등학교 상담기록 관리 시스템입니다.

## 주요 기능

- 🔐 비밀번호 인증
- 📝 상담기록 작성
- 📋 상담기록 조회 및 검색
- ✏️ 상담기록 수정
- 🗑️ 상담기록 삭제

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## Supabase 설정

### 1. Supabase 프로젝트 생성

1. [Supabase](https://supabase.com)에 가입하고 새 프로젝트를 생성합니다.
2. 프로젝트 설정에서 API URL과 API Key를 확인합니다.

### 2. 데이터베이스 테이블 생성

Supabase SQL Editor에서 다음 SQL을 실행하여 테이블을 생성합니다:

```sql
-- 상담기록 테이블 생성
CREATE TABLE counseling_records (
    id BIGSERIAL PRIMARY KEY,
    student_name TEXT NOT NULL,
    grade INTEGER NOT NULL CHECK (grade >= 1 AND grade <= 6),
    class_num INTEGER NOT NULL CHECK (class_num >= 1 AND class_num <= 20),
    consult_date DATE NOT NULL,
    consult_content TEXT NOT NULL,
    counselor TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성 (검색 성능 향상)
CREATE INDEX idx_student_name ON counseling_records(student_name);
CREATE INDEX idx_grade_class ON counseling_records(grade, class_num);
CREATE INDEX idx_consult_date ON counseling_records(consult_date);

-- RLS (Row Level Security) 정책 설정 (선택사항)
ALTER TABLE counseling_records ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기/쓰기 가능하도록 설정 (실제 운영 시에는 더 엄격한 정책 권장)
CREATE POLICY "Allow all operations" ON counseling_records
    FOR ALL
    USING (true)
    WITH CHECK (true);
```

### 3. 환경 변수 설정

#### 방법 1: Streamlit Secrets (권장)

프로젝트 루트에 `.streamlit/secrets.toml` 파일을 생성하고 다음 내용을 추가합니다:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
ADMIN_PASSWORD = "your-secure-password"
```

#### 방법 2: 환경 변수

Windows (PowerShell):
```powershell
$env:SUPABASE_URL="https://your-project.supabase.co"
$env:SUPABASE_KEY="your-anon-key"
$env:ADMIN_PASSWORD="your-secure-password"
```

Linux/Mac:
```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
export ADMIN_PASSWORD="your-secure-password"
```

## 실행 방법

```bash
streamlit run app.py
```

## 사용 방법

1. 애플리케이션 실행 후 비밀번호를 입력합니다.
2. 사이드바에서 원하는 기능을 선택합니다:
   - **상담기록 작성**: 새로운 상담기록을 작성합니다.
   - **상담기록 조회**: 저장된 상담기록을 검색하고 조회합니다.
   - **상담기록 수정**: 기존 상담기록을 수정합니다.
   - **상담기록 삭제**: 상담기록을 삭제합니다.

## 보안 주의사항

- 프로덕션 환경에서는 더 강력한 인증 시스템을 사용하세요.
- Supabase RLS 정책을 적절히 설정하여 데이터 접근을 제한하세요.
- 비밀번호는 환경 변수나 secrets로 관리하고, 코드에 하드코딩하지 마세요.

## 라이선스

MIT License

