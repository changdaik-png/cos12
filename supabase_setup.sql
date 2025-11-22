-- 초등학교 상담기록부 데이터베이스 테이블 생성 스크립트
-- Supabase SQL Editor에서 실행하세요

-- 기존 테이블 및 관련 객체 삭제 (이미 존재하는 경우)
DROP TABLE IF EXISTS counseling_records CASCADE;

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

-- RLS (Row Level Security) 정책 설정
-- 주의: 실제 운영 환경에서는 더 엄격한 정책을 설정하세요
ALTER TABLE counseling_records ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기/쓰기 가능하도록 설정
-- 프로덕션 환경에서는 인증된 사용자만 접근 가능하도록 변경하세요
DROP POLICY IF EXISTS "Allow all operations" ON counseling_records;
CREATE POLICY "Allow all operations" ON counseling_records
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 테이블 생성 확인
SELECT 'Table created successfully!' AS status;

