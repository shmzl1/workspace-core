--
-- PostgreSQL database dump
--

\restrict W2PQ0DcGixoT7pRtLZqdfT0Lpjq2jGuZFY2gVOtcaiBhJjC506rZtqfBSjla1Nk

-- Dumped from database version 16.13 (Debian 16.13-1.pgdg13+1)
-- Dumped by pg_dump version 16.13 (Debian 16.13-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO talentflow;

--
-- Name: attendance_records; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.attendance_records (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    attendance_date date NOT NULL,
    check_in_at timestamp with time zone,
    check_out_at timestamp with time zone,
    status character varying(32) DEFAULT 'NORMAL'::character varying NOT NULL,
    late_minutes integer DEFAULT 0 NOT NULL,
    early_leave_minutes integer DEFAULT 0 NOT NULL,
    leave_balance_id integer,
    source character varying(32) DEFAULT 'WEB'::character varying NOT NULL,
    remark character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_attendance_records_checkout_after_checkin CHECK (((check_out_at IS NULL) OR (check_in_at IS NULL) OR (check_out_at > check_in_at))),
    CONSTRAINT ck_attendance_records_early_leave_minutes_nonnegative CHECK ((early_leave_minutes >= 0)),
    CONSTRAINT ck_attendance_records_late_minutes_nonnegative CHECK ((late_minutes >= 0)),
    CONSTRAINT ck_attendance_records_source CHECK (((source)::text = ANY ((ARRAY['WEB'::character varying, 'MINIPROGRAM'::character varying, 'MANUAL'::character varying, 'SEED'::character varying])::text[]))),
    CONSTRAINT ck_attendance_records_status CHECK (((status)::text = ANY ((ARRAY['NORMAL'::character varying, 'LATE'::character varying, 'EARLY_LEAVE'::character varying, 'ABSENT'::character varying, 'UNPAID_LEAVE'::character varying, 'APPROVED_ANNUAL_LEAVE'::character varying])::text[])))
);


ALTER TABLE public.attendance_records OWNER TO talentflow;

--
-- Name: attendance_records_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.attendance_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.attendance_records_id_seq OWNER TO talentflow;

--
-- Name: attendance_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.attendance_records_id_seq OWNED BY public.attendance_records.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    actor_user_id integer,
    actor_role character varying(32) NOT NULL,
    target_employee_id integer,
    action character varying(64) NOT NULL,
    resource_type character varying(64) NOT NULL,
    resource_id integer,
    requested_fields jsonb DEFAULT '[]'::jsonb NOT NULL,
    result character varying(32) NOT NULL,
    reason character varying(255),
    trace_id character varying(64),
    ip_address character varying(64),
    user_agent character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_audit_logs_actor_role CHECK (((actor_role)::text = ANY ((ARRAY['EMPLOYEE'::character varying, 'HR_SPECIALIST'::character varying, 'DEPARTMENT_MANAGER'::character varying, 'PAYROLL_ADMIN'::character varying])::text[]))),
    CONSTRAINT ck_audit_logs_result CHECK (((result)::text = ANY ((ARRAY['ALLOWED'::character varying, 'DENIED'::character varying, 'SUCCESS'::character varying, 'FAILURE'::character varying])::text[])))
);


ALTER TABLE public.audit_logs OWNER TO talentflow;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO talentflow;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: candidate_applications; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.candidate_applications (
    id integer NOT NULL,
    candidate_id integer NOT NULL,
    job_id integer NOT NULL,
    current_stage character varying(32) DEFAULT 'APPLIED'::character varying NOT NULL,
    score_total numeric(6,2),
    score_breakdown jsonb DEFAULT '{}'::jsonb NOT NULL,
    weights_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    scored_at timestamp with time zone,
    applied_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_candidate_applications_current_stage CHECK (((current_stage)::text = ANY ((ARRAY['APPLIED'::character varying, 'AI_SCREENED'::character varying, 'INTERVIEW_PENDING'::character varying, 'INTERVIEWING'::character varying, 'DECISION_PENDING'::character varying, 'OFFERED'::character varying, 'HIRED'::character varying, 'REJECTED'::character varying])::text[]))),
    CONSTRAINT ck_candidate_applications_score_nonnegative CHECK (((score_total IS NULL) OR (score_total >= (0)::numeric)))
);


ALTER TABLE public.candidate_applications OWNER TO talentflow;

--
-- Name: candidate_applications_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.candidate_applications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_applications_id_seq OWNER TO talentflow;

--
-- Name: candidate_applications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.candidate_applications_id_seq OWNED BY public.candidate_applications.id;


--
-- Name: candidate_pipeline_records; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.candidate_pipeline_records (
    id integer NOT NULL,
    application_id integer NOT NULL,
    from_stage character varying(32),
    to_stage character varying(32) NOT NULL,
    note text,
    changed_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_pipeline_records_from_stage CHECK (((from_stage IS NULL) OR ((from_stage)::text = ANY ((ARRAY['APPLIED'::character varying, 'AI_SCREENED'::character varying, 'INTERVIEW_PENDING'::character varying, 'INTERVIEWING'::character varying, 'DECISION_PENDING'::character varying, 'OFFERED'::character varying, 'HIRED'::character varying, 'REJECTED'::character varying])::text[])))),
    CONSTRAINT ck_pipeline_records_to_stage CHECK (((to_stage)::text = ANY ((ARRAY['APPLIED'::character varying, 'AI_SCREENED'::character varying, 'INTERVIEW_PENDING'::character varying, 'INTERVIEWING'::character varying, 'DECISION_PENDING'::character varying, 'OFFERED'::character varying, 'HIRED'::character varying, 'REJECTED'::character varying])::text[])))
);


ALTER TABLE public.candidate_pipeline_records OWNER TO talentflow;

--
-- Name: candidate_pipeline_records_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.candidate_pipeline_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidate_pipeline_records_id_seq OWNER TO talentflow;

--
-- Name: candidate_pipeline_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.candidate_pipeline_records_id_seq OWNED BY public.candidate_pipeline_records.id;


--
-- Name: candidates; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.candidates (
    id integer NOT NULL,
    candidate_no character varying(32) NOT NULL,
    full_name character varying(100) NOT NULL,
    email character varying(255),
    phone character varying(32),
    resume_file_path character varying(500),
    resume_text text,
    skills jsonb DEFAULT '[]'::jsonb NOT NULL,
    experience_months integer DEFAULT 0 NOT NULL,
    available_from date,
    source character varying(32) DEFAULT 'MANUAL'::character varying NOT NULL,
    profile_json jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_candidates_experience_nonnegative CHECK ((experience_months >= 0)),
    CONSTRAINT ck_candidates_source CHECK (((source)::text = ANY ((ARRAY['MANUAL'::character varying, 'UPLOAD'::character varying, 'SEED'::character varying, 'REFERRAL'::character varying])::text[])))
);


ALTER TABLE public.candidates OWNER TO talentflow;

--
-- Name: candidates_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.candidates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.candidates_id_seq OWNER TO talentflow;

--
-- Name: candidates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.candidates_id_seq OWNED BY public.candidates.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    user_id integer,
    employee_no character varying(32) NOT NULL,
    full_name character varying(100) NOT NULL,
    department character varying(100) NOT NULL,
    job_title character varying(100) NOT NULL,
    manager_employee_id integer,
    email character varying(255),
    phone character varying(32),
    hire_date date,
    employment_status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_employees_employment_status CHECK (((employment_status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying, 'ON_LEAVE'::character varying])::text[])))
);


ALTER TABLE public.employees OWNER TO talentflow;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_id_seq OWNER TO talentflow;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: interview_slots; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.interview_slots (
    id integer NOT NULL,
    resource_type character varying(32) NOT NULL,
    candidate_id integer,
    interviewer_id integer,
    meeting_room_id integer,
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone NOT NULL,
    is_available boolean DEFAULT true NOT NULL,
    note character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_interview_slots_exactly_one_resource CHECK ((((((candidate_id IS NOT NULL))::integer + ((interviewer_id IS NOT NULL))::integer) + ((meeting_room_id IS NOT NULL))::integer) = 1)),
    CONSTRAINT ck_interview_slots_resource_type CHECK (((resource_type)::text = ANY ((ARRAY['CANDIDATE'::character varying, 'INTERVIEWER'::character varying, 'ROOM'::character varying])::text[]))),
    CONSTRAINT ck_interview_slots_resource_type_match CHECK (((((resource_type)::text = 'CANDIDATE'::text) AND (candidate_id IS NOT NULL) AND (interviewer_id IS NULL) AND (meeting_room_id IS NULL)) OR (((resource_type)::text = 'INTERVIEWER'::text) AND (candidate_id IS NULL) AND (interviewer_id IS NOT NULL) AND (meeting_room_id IS NULL)) OR (((resource_type)::text = 'ROOM'::text) AND (candidate_id IS NULL) AND (interviewer_id IS NULL) AND (meeting_room_id IS NOT NULL)))),
    CONSTRAINT ck_interview_slots_time_order CHECK ((end_at > start_at))
);


ALTER TABLE public.interview_slots OWNER TO talentflow;

--
-- Name: interview_slots_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.interview_slots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interview_slots_id_seq OWNER TO talentflow;

--
-- Name: interview_slots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.interview_slots_id_seq OWNED BY public.interview_slots.id;


--
-- Name: interviewers; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.interviewers (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    specialties jsonb DEFAULT '[]'::jsonb NOT NULL,
    max_interviews_per_day integer DEFAULT 4 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_interviewers_max_per_day_positive CHECK ((max_interviews_per_day > 0))
);


ALTER TABLE public.interviewers OWNER TO talentflow;

--
-- Name: interviewers_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.interviewers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interviewers_id_seq OWNER TO talentflow;

--
-- Name: interviewers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.interviewers_id_seq OWNED BY public.interviewers.id;


--
-- Name: interviews; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.interviews (
    id integer NOT NULL,
    application_id integer NOT NULL,
    interviewer_id integer NOT NULL,
    meeting_room_id integer NOT NULL,
    start_at timestamp with time zone NOT NULL,
    end_at timestamp with time zone NOT NULL,
    status character varying(32) DEFAULT 'SCHEDULED'::character varying NOT NULL,
    conflict_explanation jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_interviews_status CHECK (((status)::text = ANY ((ARRAY['SCHEDULED'::character varying, 'COMPLETED'::character varying, 'CANCELLED'::character varying])::text[]))),
    CONSTRAINT ck_interviews_time_order CHECK ((end_at > start_at))
);


ALTER TABLE public.interviews OWNER TO talentflow;

--
-- Name: interviews_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.interviews_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interviews_id_seq OWNER TO talentflow;

--
-- Name: interviews_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.interviews_id_seq OWNED BY public.interviews.id;


--
-- Name: jobs; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.jobs (
    id integer NOT NULL,
    job_code character varying(32) NOT NULL,
    title character varying(150) NOT NULL,
    department character varying(100) NOT NULL,
    description text,
    required_skills jsonb DEFAULT '[]'::jsonb NOT NULL,
    preferred_skills jsonb DEFAULT '[]'::jsonb NOT NULL,
    min_experience_months integer DEFAULT 0 NOT NULL,
    location character varying(100),
    employment_type character varying(32) DEFAULT 'INTERN'::character varying NOT NULL,
    status character varying(32) DEFAULT 'DRAFT'::character varying NOT NULL,
    owner_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_jobs_employment_type CHECK (((employment_type)::text = ANY ((ARRAY['INTERN'::character varying, 'FULL_TIME'::character varying, 'PART_TIME'::character varying])::text[]))),
    CONSTRAINT ck_jobs_min_experience_nonnegative CHECK ((min_experience_months >= 0)),
    CONSTRAINT ck_jobs_status CHECK (((status)::text = ANY ((ARRAY['DRAFT'::character varying, 'OPEN'::character varying, 'CLOSED'::character varying])::text[])))
);


ALTER TABLE public.jobs OWNER TO talentflow;

--
-- Name: jobs_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.jobs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.jobs_id_seq OWNER TO talentflow;

--
-- Name: jobs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.jobs_id_seq OWNED BY public.jobs.id;


--
-- Name: leave_balances; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.leave_balances (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    leave_type character varying(32) DEFAULT 'ANNUAL'::character varying NOT NULL,
    year integer NOT NULL,
    total_days numeric(5,2) NOT NULL,
    used_days numeric(5,2) DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_leave_balances_leave_type CHECK (((leave_type)::text = 'ANNUAL'::text)),
    CONSTRAINT ck_leave_balances_total_days_nonnegative CHECK ((total_days >= (0)::numeric)),
    CONSTRAINT ck_leave_balances_used_days_lte_total CHECK ((used_days <= total_days)),
    CONSTRAINT ck_leave_balances_used_days_nonnegative CHECK ((used_days >= (0)::numeric))
);


ALTER TABLE public.leave_balances OWNER TO talentflow;

--
-- Name: leave_balances_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.leave_balances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.leave_balances_id_seq OWNER TO talentflow;

--
-- Name: leave_balances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.leave_balances_id_seq OWNED BY public.leave_balances.id;


--
-- Name: meeting_rooms; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.meeting_rooms (
    id integer NOT NULL,
    room_code character varying(32) NOT NULL,
    name character varying(100) NOT NULL,
    location character varying(100),
    capacity integer DEFAULT 1 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_meeting_rooms_capacity_positive CHECK ((capacity > 0))
);


ALTER TABLE public.meeting_rooms OWNER TO talentflow;

--
-- Name: meeting_rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.meeting_rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.meeting_rooms_id_seq OWNER TO talentflow;

--
-- Name: meeting_rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.meeting_rooms_id_seq OWNED BY public.meeting_rooms.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    notification_type character varying(64) NOT NULL,
    title character varying(200) NOT NULL,
    content text,
    payload jsonb DEFAULT '{}'::jsonb NOT NULL,
    is_read boolean DEFAULT false NOT NULL,
    read_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO talentflow;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notifications_id_seq OWNER TO talentflow;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: payroll_adjustments; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.payroll_adjustments (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    payroll_period_id integer NOT NULL,
    adjustment_type character varying(32) NOT NULL,
    amount numeric(12,2) NOT NULL,
    reason character varying(255),
    created_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payroll_adjustments_amount_nonnegative CHECK ((amount >= (0)::numeric)),
    CONSTRAINT ck_payroll_adjustments_type CHECK (((adjustment_type)::text = ANY ((ARRAY['PERFORMANCE_BONUS'::character varying, 'TRANSPORT_ALLOWANCE'::character varying, 'MEAL_ALLOWANCE'::character varying, 'MANUAL_EARNING'::character varying, 'MANUAL_DEDUCTION'::character varying])::text[])))
);


ALTER TABLE public.payroll_adjustments OWNER TO talentflow;

--
-- Name: payroll_adjustments_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.payroll_adjustments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payroll_adjustments_id_seq OWNER TO talentflow;

--
-- Name: payroll_adjustments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.payroll_adjustments_id_seq OWNED BY public.payroll_adjustments.id;


--
-- Name: payroll_line_items; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.payroll_line_items (
    id integer NOT NULL,
    payroll_review_record_id integer NOT NULL,
    payroll_rule_id integer,
    item_type character varying(32) NOT NULL,
    item_name character varying(100) NOT NULL,
    amount numeric(12,2) NOT NULL,
    source_type character varying(32),
    source_reference_json jsonb DEFAULT '{}'::jsonb NOT NULL,
    calculation_detail_json jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payroll_line_items_amount_nonnegative CHECK ((amount >= (0)::numeric)),
    CONSTRAINT ck_payroll_line_items_item_type CHECK (((item_type)::text = ANY ((ARRAY['EARNING'::character varying, 'DEDUCTION'::character varying])::text[]))),
    CONSTRAINT ck_payroll_line_items_source_type CHECK (((source_type IS NULL) OR ((source_type)::text = ANY ((ARRAY['ATTENDANCE'::character varying, 'PAYROLL_ADJUSTMENT'::character varying, 'MANUAL'::character varying, 'RULE'::character varying])::text[]))))
);


ALTER TABLE public.payroll_line_items OWNER TO talentflow;

--
-- Name: payroll_line_items_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.payroll_line_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payroll_line_items_id_seq OWNER TO talentflow;

--
-- Name: payroll_line_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.payroll_line_items_id_seq OWNED BY public.payroll_line_items.id;


--
-- Name: payroll_periods; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.payroll_periods (
    id integer NOT NULL,
    period_code character varying(32) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    standard_work_days numeric(5,2) NOT NULL,
    status character varying(32) DEFAULT 'OPEN'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payroll_periods_date_range CHECK ((end_date >= start_date)),
    CONSTRAINT ck_payroll_periods_standard_work_days_positive CHECK ((standard_work_days > (0)::numeric)),
    CONSTRAINT ck_payroll_periods_status CHECK (((status)::text = ANY ((ARRAY['OPEN'::character varying, 'CLOSED'::character varying])::text[])))
);


ALTER TABLE public.payroll_periods OWNER TO talentflow;

--
-- Name: payroll_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.payroll_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payroll_periods_id_seq OWNER TO talentflow;

--
-- Name: payroll_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.payroll_periods_id_seq OWNED BY public.payroll_periods.id;


--
-- Name: payroll_review_records; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.payroll_review_records (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    payroll_period_id integer NOT NULL,
    salary_record_id integer,
    status character varying(32) DEFAULT 'DRAFT'::character varying NOT NULL,
    base_salary_snapshot numeric(12,2) NOT NULL,
    standard_work_days_snapshot numeric(5,2) NOT NULL,
    calculation_snapshot jsonb DEFAULT '{}'::jsonb NOT NULL,
    total_earnings numeric(12,2) DEFAULT 0 NOT NULL,
    total_deductions numeric(12,2) DEFAULT 0 NOT NULL,
    net_salary_preview numeric(12,2) DEFAULT 0 NOT NULL,
    generated_by_user_id integer,
    confirmed_by_user_id integer,
    confirmed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payroll_review_records_base_salary_nonnegative CHECK ((base_salary_snapshot >= (0)::numeric)),
    CONSTRAINT ck_payroll_review_records_confirmed_fields CHECK ((((status)::text <> 'CONFIRMED'::text) OR ((confirmed_by_user_id IS NOT NULL) AND (confirmed_at IS NOT NULL)))),
    CONSTRAINT ck_payroll_review_records_deductions_nonnegative CHECK ((total_deductions >= (0)::numeric)),
    CONSTRAINT ck_payroll_review_records_earnings_nonnegative CHECK ((total_earnings >= (0)::numeric)),
    CONSTRAINT ck_payroll_review_records_net_nonnegative CHECK ((net_salary_preview >= (0)::numeric)),
    CONSTRAINT ck_payroll_review_records_status CHECK (((status)::text = ANY ((ARRAY['DRAFT'::character varying, 'PRE_AUDIT_GENERATED'::character varying, 'PENDING_HR_CONFIRMATION'::character varying, 'CONFIRMED'::character varying])::text[]))),
    CONSTRAINT ck_payroll_review_records_work_days_positive CHECK ((standard_work_days_snapshot > (0)::numeric))
);


ALTER TABLE public.payroll_review_records OWNER TO talentflow;

--
-- Name: payroll_review_records_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.payroll_review_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payroll_review_records_id_seq OWNER TO talentflow;

--
-- Name: payroll_review_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.payroll_review_records_id_seq OWNED BY public.payroll_review_records.id;


--
-- Name: payroll_rules; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.payroll_rules (
    id integer NOT NULL,
    rule_code character varying(32) NOT NULL,
    name character varying(100) NOT NULL,
    direction character varying(16) NOT NULL,
    applies_to character varying(32) NOT NULL,
    calculation_method character varying(32) NOT NULL,
    formula_description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_payroll_rules_applies_to CHECK (((applies_to)::text = ANY ((ARRAY['BASE_SALARY'::character varying, 'PERFORMANCE_BONUS'::character varying, 'TRANSPORT_ALLOWANCE'::character varying, 'MEAL_ALLOWANCE'::character varying, 'ABSENCE'::character varying, 'LATE'::character varying, 'EARLY_LEAVE'::character varying, 'UNPAID_LEAVE'::character varying])::text[]))),
    CONSTRAINT ck_payroll_rules_calculation_method CHECK (((calculation_method)::text = ANY ((ARRAY['FIXED_AMOUNT'::character varying, 'PER_DAY'::character varying, 'PER_OCCURRENCE'::character varying, 'MANUAL'::character varying])::text[]))),
    CONSTRAINT ck_payroll_rules_direction CHECK (((direction)::text = ANY ((ARRAY['EARNING'::character varying, 'DEDUCTION'::character varying])::text[])))
);


ALTER TABLE public.payroll_rules OWNER TO talentflow;

--
-- Name: payroll_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.payroll_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.payroll_rules_id_seq OWNER TO talentflow;

--
-- Name: payroll_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.payroll_rules_id_seq OWNED BY public.payroll_rules.id;


--
-- Name: policy_documents; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.policy_documents (
    id integer NOT NULL,
    document_code character varying(64) NOT NULL,
    title character varying(200) NOT NULL,
    category character varying(64) NOT NULL,
    source_path character varying(500),
    version character varying(32),
    is_active boolean DEFAULT true NOT NULL,
    metadata_json jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.policy_documents OWNER TO talentflow;

--
-- Name: policy_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.policy_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.policy_documents_id_seq OWNER TO talentflow;

--
-- Name: policy_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.policy_documents_id_seq OWNED BY public.policy_documents.id;


--
-- Name: salary_records; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.salary_records (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    base_salary numeric(12,2) NOT NULL,
    currency character varying(16) DEFAULT 'CNY'::character varying NOT NULL,
    effective_from date NOT NULL,
    effective_to date,
    created_by_user_id integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_salary_records_base_salary_nonnegative CHECK ((base_salary >= (0)::numeric)),
    CONSTRAINT ck_salary_records_effective_range CHECK (((effective_to IS NULL) OR (effective_to >= effective_from)))
);


ALTER TABLE public.salary_records OWNER TO talentflow;

--
-- Name: salary_records_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.salary_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.salary_records_id_seq OWNER TO talentflow;

--
-- Name: salary_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.salary_records_id_seq OWNED BY public.salary_records.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(64) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(32) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_users_role CHECK (((role)::text = ANY ((ARRAY['EMPLOYEE'::character varying, 'HR_SPECIALIST'::character varying, 'DEPARTMENT_MANAGER'::character varying, 'PAYROLL_ADMIN'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO talentflow;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO talentflow;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: work_calendars; Type: TABLE; Schema: public; Owner: talentflow
--

CREATE TABLE public.work_calendars (
    id integer NOT NULL,
    calendar_date date NOT NULL,
    is_workday boolean DEFAULT true NOT NULL,
    standard_check_in_time time without time zone DEFAULT '09:00:00'::time without time zone NOT NULL,
    standard_check_out_time time without time zone DEFAULT '18:00:00'::time without time zone NOT NULL,
    late_grace_minutes integer DEFAULT 0 NOT NULL,
    holiday_name character varying(100),
    remark character varying(255),
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_work_calendars_late_grace_nonnegative CHECK ((late_grace_minutes >= 0))
);


ALTER TABLE public.work_calendars OWNER TO talentflow;

--
-- Name: work_calendars_id_seq; Type: SEQUENCE; Schema: public; Owner: talentflow
--

CREATE SEQUENCE public.work_calendars_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.work_calendars_id_seq OWNER TO talentflow;

--
-- Name: work_calendars_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: talentflow
--

ALTER SEQUENCE public.work_calendars_id_seq OWNED BY public.work_calendars.id;


--
-- Name: attendance_records id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.attendance_records ALTER COLUMN id SET DEFAULT nextval('public.attendance_records_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: candidate_applications id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_applications ALTER COLUMN id SET DEFAULT nextval('public.candidate_applications_id_seq'::regclass);


--
-- Name: candidate_pipeline_records id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_pipeline_records ALTER COLUMN id SET DEFAULT nextval('public.candidate_pipeline_records_id_seq'::regclass);


--
-- Name: candidates id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidates ALTER COLUMN id SET DEFAULT nextval('public.candidates_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: interview_slots id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interview_slots ALTER COLUMN id SET DEFAULT nextval('public.interview_slots_id_seq'::regclass);


--
-- Name: interviewers id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviewers ALTER COLUMN id SET DEFAULT nextval('public.interviewers_id_seq'::regclass);


--
-- Name: interviews id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviews ALTER COLUMN id SET DEFAULT nextval('public.interviews_id_seq'::regclass);


--
-- Name: jobs id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.jobs ALTER COLUMN id SET DEFAULT nextval('public.jobs_id_seq'::regclass);


--
-- Name: leave_balances id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.leave_balances ALTER COLUMN id SET DEFAULT nextval('public.leave_balances_id_seq'::regclass);


--
-- Name: meeting_rooms id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.meeting_rooms ALTER COLUMN id SET DEFAULT nextval('public.meeting_rooms_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: payroll_adjustments id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_adjustments ALTER COLUMN id SET DEFAULT nextval('public.payroll_adjustments_id_seq'::regclass);


--
-- Name: payroll_line_items id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_line_items ALTER COLUMN id SET DEFAULT nextval('public.payroll_line_items_id_seq'::regclass);


--
-- Name: payroll_periods id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_periods ALTER COLUMN id SET DEFAULT nextval('public.payroll_periods_id_seq'::regclass);


--
-- Name: payroll_review_records id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records ALTER COLUMN id SET DEFAULT nextval('public.payroll_review_records_id_seq'::regclass);


--
-- Name: payroll_rules id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_rules ALTER COLUMN id SET DEFAULT nextval('public.payroll_rules_id_seq'::regclass);


--
-- Name: policy_documents id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.policy_documents ALTER COLUMN id SET DEFAULT nextval('public.policy_documents_id_seq'::regclass);


--
-- Name: salary_records id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.salary_records ALTER COLUMN id SET DEFAULT nextval('public.salary_records_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: work_calendars id; Type: DEFAULT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.work_calendars ALTER COLUMN id SET DEFAULT nextval('public.work_calendars_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.alembic_version (version_num) FROM stdin;
0001_initial_schema
\.


--
-- Data for Name: attendance_records; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.attendance_records (id, employee_id, attendance_date, check_in_at, check_out_at, status, late_minutes, early_leave_minutes, leave_balance_id, source, remark, created_at, updated_at) FROM stdin;
6	1	2026-07-09	2026-07-09 09:58:54.601069+00	2026-07-09 10:01:08.342043+00	LATE	58	479	\N	WEB	\N	2026-07-09 01:58:54.594476+00	2026-07-09 02:01:08.335484+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.audit_logs (id, actor_user_id, actor_role, target_employee_id, action, resource_type, resource_id, requested_fields, result, reason, trace_id, ip_address, user_agent, created_at) FROM stdin;
53	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	1377169e4d8142028e5ad46fc771a5b8	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:00:59.994519+00
54	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	8ba1864245bb44c695b55d92f26832f9	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:01:05.223944+00
55	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	eee3d2651f5441efbcbf8ac8e6d96fac	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:01:52.124037+00
56	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	09211c01ff4b4f49ae26a77f44e0c50a	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:01:54.767307+00
57	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	d50cb48e163c431592272e50d6971b95	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:01:58.072682+00
58	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	69c96263e7834fa99c1eb38acebde058	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:02:14.028182+00
59	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	3dea21e9582e4be397d0a57e30dbc742	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:02:19.097803+00
60	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	90bf756a78c7416399c626226ef6d6b7	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:02:20.696235+00
61	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	ba67c3a9709c4bc6b70635f9a4fcc512	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:14:10.27081+00
62	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	049c9206fa57404e8cec86469f46ef46	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 02:14:12.618667+00
104	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	b3b8bc0a3ce247038d06a496fa142678	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:25.106411+00
105	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	40c54123992f4591b96611334895f09d	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:27.424824+00
106	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	467c7e8ec8d743e6ad195506f4970716	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:29.626232+00
107	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	af19469a4dbc4a6d90588b6e2ed5bf2d	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:31.537771+00
108	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	f25331cb3bba45ef9a0c5a36cc979227	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:34.837434+00
109	1	EMPLOYEE	3	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	fc08f68cd61c4684b385394dc33a5dc7	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:37.270579+00
110	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	a65834b031654c7ea94086c36321031f	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:52:43.740654+00
63	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	b1e710b3a85847e7980affe5efbc6f3c	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:34.827111+00
64	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	171536ab9c3c4829be506eca075b6a97	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:36.279804+00
65	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	d9965f0c04ba47acbb088ef7befa4930	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:36.899548+00
66	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	f27466d2de7a4bbf8102e42115e19b78	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:37.271472+00
67	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	93c1bf8a7336457a80cc4298ceca4ef1	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:37.597763+00
68	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	32f064256917429495bab1dd81b73cf1	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:41.742138+00
69	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	e0aae441b6a74121b6cb67452e5c16a2	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:41.965241+00
70	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	5162242e76c74c878f95121eb02e1cfa	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:47.680114+00
71	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	fa63676376264c05b0a61631d6a719ed	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:47:55.598005+00
72	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	8b3adf77b35c43508b0bb36736bec19a	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:48:00.849168+00
73	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	ebf8395021d3459f9a6810a08a3c6ff7	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:48:03.624178+00
74	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	919829f38a9f4270903063aa6af1694e	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:48:11.430549+00
75	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	a8e123883b8f4ecd9d757b705cd865e4	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:48:12.69373+00
76	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	bd640b20fe44418ea5b6b17d41413e17	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:48:14.943325+00
77	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	9b2218a79e224f17a49b6f586f48773a	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 06:49:26.696816+00
111	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	d055305f19b94b8a8bdf149daabb4990	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:54:09.679201+00
112	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	038c08a320924e179ece3d2b05856af7	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:54:10.078553+00
78	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	2ded2aa687164e56b7f2cb996a502cc2	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:03:29.785397+00
82	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	62fb96274de446e28d2d243899a18ce6	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:26.858026+00
84	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	5aba0d5ec7a34c09977c238239ac95ca	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:29.368043+00
85	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	46aa2d09af3a4b79a12b0c81198df375	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:31.404383+00
87	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	94eda7b4549b40fd9de765216f960e93	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:33.432689+00
88	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	fd638465a8534e34bc6bc75d90239d65	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:15:58.724478+00
90	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	30532c02332144b3964de3e888260af3	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:16:39.065875+00
91	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	c508c8031f394406963928ad99db522e	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:16:40.245118+00
92	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	4999cdb259fb4b648f48e757393b5c06	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:23:37.474634+00
93	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	1426f330a1634658837bcb0d03ce0b24	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:23:37.529278+00
94	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	e7840dc5140a49c883c4dd0a79b49153	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:23:40.296232+00
79	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	232ff60c91d5477f8e4046fa9ce87b86	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:03:40.094274+00
80	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	0a8ff2b45d134d93a7495e8d1ef91b1d	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:03:46.613262+00
81	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	e6631588961d4b829c4657c364158bc1	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:21.122316+00
83	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	693b64db872c4436bc9ef9cc8a5c1972	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:27.803348+00
86	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	56598af2f1ce477385973bb4408f0a68	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:04:32.513486+00
89	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	6af6aca2e72541c4a3a8be5ea222203e	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:16:00.065831+00
2	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	\N	testclient	testclient	2026-07-08 03:51:09.175283+00
6	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	\N	127.0.0.1	python-httpx/0.28.1	2026-07-08 03:52:32.318571+00
23	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	\N	testclient	testclient	2026-07-08 06:39:26.513342+00
27	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	\N	testclient	testclient	2026-07-08 06:40:57.679785+00
34	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:53:45.484473+00
1	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	testclient	testclient	2026-07-08 03:51:09.150858+00
5	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	python-httpx/0.28.1	2026-07-08 03:52:22.510102+00
8	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 03:59:04.680049+00
9	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 05:59:41.5822+00
10	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:08:23.869756+00
11	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:08:44.753772+00
12	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:10:30.681332+00
13	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:10:30.950011+00
14	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:11:54.814644+00
15	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:17:51.618164+00
16	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:18:46.597845+00
17	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:31:12.987558+00
18	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:33:24.942154+00
19	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:33:28.098485+00
20	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:33:32.500784+00
21	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36	2026-07-08 06:33:34.083697+00
22	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	testclient	testclient	2026-07-08 06:39:26.472661+00
26	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	testclient	testclient	2026-07-08 06:40:57.652495+00
30	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:53:31.166315+00
31	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:53:35.301971+00
32	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:53:37.25309+00
33	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:53:38.511702+00
35	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 06:53:48.933327+00
36	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 07:10:31.65387+00
37	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	\N	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 07:10:34.529142+00
38	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	f50f68ac035f45db89148553c67376c0	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:16:41.145979+00
39	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	fdd00da44c004e2f9bc11da3d2987a25	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:16:43.818856+00
40	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	d59a46fec5a34a05860c9055353b2397	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:16:45.231529+00
41	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	afa8d2f4bda64fc08e190d367707bcde	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:19:59.974817+00
42	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	a90e1c6e94234640984bdcca1a23a013	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:20:01.87037+00
43	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	4b8eefbf858942f6884c160164f7f07b	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:20:03.280424+00
44	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	fef27da30fa74b78bed324f883779172	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:23:14.635895+00
45	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	842bd67e42744c3e83155a48505dee05	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:23:17.308565+00
46	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	da9a94d85c804956ba6aede29f650485	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:23:18.983547+00
47	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	964a85dd9cae42e29a80fed8858aef03	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 08:23:20.699998+00
48	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	7470c443113645bea69e5c87a0f08259	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 09:57:41.131311+00
49	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	8dd1a4da46774e96aff7b692848e5c75	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 09:57:43.692918+00
50	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	07d047605f9749f2a5f9cfe05b3e9242	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 09:57:45.122224+00
51	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	be4c7d7bf7b049bca4b4130ccf413a87	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 10:01:27.523423+00
52	\N	EMPLOYEE	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	debad3c2377c4c2889d4056a64821601	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-08 10:27:39.857506+00
3	\N	DEPARTMENT_MANAGER	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛柈銊╂，缂佸繒鎮婇弻銉嚄閺堫剟鍎撮梻銊ユ喅瀹搞儴鏌傜挧鍕繆閹垽绱欐禒鍛唨閺堫剙浼愮挧鍕瑢鐢胶顫掗敍?\N	testclient	testclient	2026-07-08 03:51:09.196458+00
7	\N	DEPARTMENT_MANAGER	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛柈銊╂，缂佸繒鎮婇弻銉嚄閺堫剟鍎撮梻銊ユ喅瀹搞儴鏌傜挧鍕繆閹垽绱欐禒鍛唨閺堫剙浼愮挧鍕瑢鐢胶顫掗敍?\N	127.0.0.1	python-httpx/0.28.1	2026-07-08 03:52:39.992723+00
24	\N	DEPARTMENT_MANAGER	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛柈銊╂，缂佸繒鎮婇弻銉嚄閺堫剟鍎撮梻銊ユ喅瀹搞儴鏌傜挧鍕繆閹垽绱欐禒鍛唨閺堫剙浼愮挧鍕瑢鐢胶顫掗敍?\N	testclient	testclient	2026-07-08 06:39:26.537473+00
28	\N	DEPARTMENT_MANAGER	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛柈銊╂，缂佸繒鎮婇弻銉嚄閺堫剟鍎撮梻銊ユ喅瀹搞儴鏌傜挧鍕繆閹垽绱欐禒鍛唨閺堫剙浼愮挧鍕瑢鐢胶顫掗敍?\N	testclient	testclient	2026-07-08 06:40:57.702939+00
4	\N	PAYROLL_ADMIN	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛挅顏堝彆缁狅紕鎮婇崨妯荤叀鐠囥垺澧嶉張澶庢焸鐠у嫪淇婇幁?\N	testclient	testclient	2026-07-08 03:51:09.213594+00
25	\N	PAYROLL_ADMIN	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛挅顏堝彆缁狅紕鎮婇崨妯荤叀鐠囥垺澧嶉張澶庢焸鐠у嫪淇婇幁?\N	testclient	testclient	2026-07-08 06:39:26.56916+00
29	\N	PAYROLL_ADMIN	\N	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛挅顏堝彆缁狅紕鎮婇崨妯荤叀鐠囥垺澧嶉張澶庢焸鐠у嫪淇婇幁?\N	testclient	testclient	2026-07-08 06:40:57.73735+00
95	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	6ee1122f647444e189ee0cd48c7db80c	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:48:55.475924+00
96	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	c43def46c549479b994b1c2cdcffc005	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:48:55.61313+00
97	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	64f6357007d34759a010419401e44e66	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:48:59.1711+00
98	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	97a1cdfe8ca846c88e3b10a393f791f7	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:49:02.440821+00
99	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	effeb53479464d3e933aca6978383e10	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:50:04.925645+00
100	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	949aca21579d453ca14612da3e0f3915	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:50:09.703895+00
101	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	8b8e2a151bf242d5b75fb57329dff939	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:50:10.882416+00
102	1	EMPLOYEE	2	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	DENIED	閺冪姵娼堢拋鍧楁６濮濄倕鎲冲銉ф畱閽栴亣绁弫鐗堝祦	fab6ce5e2c064d6ea8da215f8f8f774c	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:50:13.31383+00
103	1	EMPLOYEE	1	QUERY_SALARY	SALARY	\N	["base_salary", "currency", "effective_from", "effective_to"]	ALLOWED	閸忎浇顔忛崨妯轰紣閺屻儴顕楅張顑挎眽閽栴亣绁穱鈩冧紖	7c1a66778f5d4963b0c07d2e9b0da3aa	127.0.0.1	Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0	2026-07-09 07:50:15.569029+00
\.


--
-- Data for Name: candidate_applications; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.candidate_applications (id, candidate_id, job_id, current_stage, score_total, score_breakdown, weights_snapshot, scored_at, applied_at, updated_at) FROM stdin;
\.


--
-- Data for Name: candidate_pipeline_records; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.candidate_pipeline_records (id, application_id, from_stage, to_stage, note, changed_by_user_id, created_at) FROM stdin;
\.


--
-- Data for Name: candidates; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.candidates (id, candidate_no, full_name, email, phone, resume_file_path, resume_text, skills, experience_months, available_from, source, profile_json, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.employees (id, user_id, employee_no, full_name, department, job_title, manager_employee_id, email, phone, hire_date, employment_status, created_at, updated_at) FROM stdin;
2	2	EMP002	閺夊孩妲?閻柨褰傞柈?閻柨褰傜紒蹇曟倞	\N	\N	\N	\N	ACTIVE	2026-07-09 01:57:51.390637+00	2026-07-09 01:57:51.390637+00
1	1	EMP001	瀵姳绱?閻柨褰傞柈?妤傛楠囧鈧崣鎴濅紣缁嬪绗€	2	\N	\N	\N	ACTIVE	2026-07-09 01:57:51.405977+00	2026-07-09 01:57:51.405977+00
3	3	EMP003	閺嬫娲﹂弲?娴滃搫濮忕挧鍕爱闁?HR娑撴挸鎲?\N	\N	\N	\N	ACTIVE	2026-07-09 01:57:51.405977+00	2026-07-09 01:57:51.405977+00
4	4	EMP004	閻滃宸?鐠愩垹濮熼柈?閽栴亪鍙曠粻锛勬倞閸?\N	\N	\N	\N	ACTIVE	2026-07-09 01:57:51.405977+00	2026-07-09 01:57:51.405977+00
\.


--
-- Data for Name: interview_slots; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.interview_slots (id, resource_type, candidate_id, interviewer_id, meeting_room_id, start_at, end_at, is_available, note, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: interviewers; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.interviewers (id, employee_id, specialties, max_interviews_per_day, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: interviews; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.interviews (id, application_id, interviewer_id, meeting_room_id, start_at, end_at, status, conflict_explanation, created_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: jobs; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.jobs (id, job_code, title, department, description, required_skills, preferred_skills, min_experience_months, location, employment_type, status, owner_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: leave_balances; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.leave_balances (id, employee_id, leave_type, year, total_days, used_days, created_at, updated_at) FROM stdin;
3	1	ANNUAL	2026	10.00	0.00	2026-07-09 01:57:51.422205+00	2026-07-09 01:57:51.422205+00
4	2	ANNUAL	2026	15.00	0.00	2026-07-09 01:57:51.422205+00	2026-07-09 01:57:51.422205+00
\.


--
-- Data for Name: meeting_rooms; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.meeting_rooms (id, room_code, name, location, capacity, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.notifications (id, user_id, notification_type, title, content, payload, is_read, read_at, created_at) FROM stdin;
\.


--
-- Data for Name: payroll_adjustments; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.payroll_adjustments (id, employee_id, payroll_period_id, adjustment_type, amount, reason, created_by_user_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payroll_line_items; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.payroll_line_items (id, payroll_review_record_id, payroll_rule_id, item_type, item_name, amount, source_type, source_reference_json, calculation_detail_json, created_at) FROM stdin;
\.


--
-- Data for Name: payroll_periods; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.payroll_periods (id, period_code, start_date, end_date, standard_work_days, status, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payroll_review_records; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.payroll_review_records (id, employee_id, payroll_period_id, salary_record_id, status, base_salary_snapshot, standard_work_days_snapshot, calculation_snapshot, total_earnings, total_deductions, net_salary_preview, generated_by_user_id, confirmed_by_user_id, confirmed_at, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: payroll_rules; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.payroll_rules (id, rule_code, name, direction, applies_to, calculation_method, formula_description, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: policy_documents; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.policy_documents (id, document_code, title, category, source_path, version, is_active, metadata_json, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: salary_records; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.salary_records (id, employee_id, base_salary, currency, effective_from, effective_to, created_by_user_id, created_at, updated_at) FROM stdin;
5	1	25000.00	CNY	2026-01-01	\N	4	2026-07-09 01:57:51.43233+00	2026-07-09 01:57:51.43233+00
6	2	35000.00	CNY	2026-01-01	\N	4	2026-07-09 01:57:51.43233+00	2026-07-09 01:57:51.43233+00
7	3	18000.00	CNY	2026-01-01	\N	4	2026-07-09 01:57:51.43233+00	2026-07-09 01:57:51.43233+00
8	4	20000.00	CNY	2026-01-01	\N	4	2026-07-09 01:57:51.43233+00	2026-07-09 01:57:51.43233+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.users (id, username, password_hash, role, is_active, created_at, updated_at) FROM stdin;
1	zhangwei	$2b$12$lWe6nY6s6./q0UKwjgz9LO69yfZ1DoiUlJiP94pUjr6oBGc4oSxBm	EMPLOYEE	t	2026-07-09 01:57:51.3695+00	2026-07-09 01:57:51.3695+00
2	liming	$2b$12$lWe6nY6s6./q0UKwjgz9LO69yfZ1DoiUlJiP94pUjr6oBGc4oSxBm	DEPARTMENT_MANAGER	t	2026-07-09 01:57:51.3695+00	2026-07-09 01:57:51.3695+00
3	linyuqing	$2b$12$lWe6nY6s6./q0UKwjgz9LO69yfZ1DoiUlJiP94pUjr6oBGc4oSxBm	HR_SPECIALIST	t	2026-07-09 01:57:51.3695+00	2026-07-09 01:57:51.3695+00
4	wangqiang	$2b$12$lWe6nY6s6./q0UKwjgz9LO69yfZ1DoiUlJiP94pUjr6oBGc4oSxBm	PAYROLL_ADMIN	t	2026-07-09 01:57:51.3695+00	2026-07-09 01:57:51.3695+00
\.


--
-- Data for Name: work_calendars; Type: TABLE DATA; Schema: public; Owner: talentflow
--

COPY public.work_calendars (id, calendar_date, is_workday, standard_check_in_time, standard_check_out_time, late_grace_minutes, holiday_name, remark, created_at, updated_at) FROM stdin;
16	2026-07-02	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
17	2026-07-03	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
18	2026-07-04	f	09:00:00	18:00:00	0	閸涖劍婀导鎴炰紖	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
19	2026-07-05	f	09:00:00	18:00:00	0	閸涖劍婀导鎴炰紖	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
20	2026-07-06	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
21	2026-07-07	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
22	2026-07-08	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
23	2026-07-09	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
24	2026-07-10	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
25	2026-07-11	f	09:00:00	18:00:00	0	閸涖劍婀导鎴炰紖	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
26	2026-07-12	f	09:00:00	18:00:00	0	閸涖劍婀导鎴炰紖	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
27	2026-07-13	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
28	2026-07-14	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
29	2026-07-15	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
30	2026-07-16	t	09:00:00	18:00:00	0	\N	\N	2026-07-09 01:57:51.44611+00	2026-07-09 01:57:51.44611+00
\.


--
-- Name: attendance_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.attendance_records_id_seq', 6, true);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 112, true);


--
-- Name: candidate_applications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.candidate_applications_id_seq', 1, false);


--
-- Name: candidate_pipeline_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.candidate_pipeline_records_id_seq', 1, false);


--
-- Name: candidates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.candidates_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.employees_id_seq', 1, false);


--
-- Name: interview_slots_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.interview_slots_id_seq', 1, false);


--
-- Name: interviewers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.interviewers_id_seq', 1, false);


--
-- Name: interviews_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.interviews_id_seq', 1, false);


--
-- Name: jobs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.jobs_id_seq', 1, false);


--
-- Name: leave_balances_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.leave_balances_id_seq', 4, true);


--
-- Name: meeting_rooms_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.meeting_rooms_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: payroll_adjustments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.payroll_adjustments_id_seq', 1, false);


--
-- Name: payroll_line_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.payroll_line_items_id_seq', 1, false);


--
-- Name: payroll_periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.payroll_periods_id_seq', 1, false);


--
-- Name: payroll_review_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.payroll_review_records_id_seq', 1, false);


--
-- Name: payroll_rules_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.payroll_rules_id_seq', 1, false);


--
-- Name: policy_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.policy_documents_id_seq', 1, false);


--
-- Name: salary_records_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.salary_records_id_seq', 8, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: work_calendars_id_seq; Type: SEQUENCE SET; Schema: public; Owner: talentflow
--

SELECT pg_catalog.setval('public.work_calendars_id_seq', 30, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: attendance_records attendance_records_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.attendance_records
    ADD CONSTRAINT attendance_records_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: candidate_applications candidate_applications_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_applications
    ADD CONSTRAINT candidate_applications_pkey PRIMARY KEY (id);


--
-- Name: candidate_pipeline_records candidate_pipeline_records_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_pipeline_records
    ADD CONSTRAINT candidate_pipeline_records_pkey PRIMARY KEY (id);


--
-- Name: candidates candidates_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT candidates_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: interview_slots interview_slots_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interview_slots
    ADD CONSTRAINT interview_slots_pkey PRIMARY KEY (id);


--
-- Name: interviewers interviewers_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviewers
    ADD CONSTRAINT interviewers_pkey PRIMARY KEY (id);


--
-- Name: interviews interviews_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_pkey PRIMARY KEY (id);


--
-- Name: jobs jobs_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_pkey PRIMARY KEY (id);


--
-- Name: leave_balances leave_balances_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.leave_balances
    ADD CONSTRAINT leave_balances_pkey PRIMARY KEY (id);


--
-- Name: meeting_rooms meeting_rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.meeting_rooms
    ADD CONSTRAINT meeting_rooms_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: payroll_adjustments payroll_adjustments_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_adjustments
    ADD CONSTRAINT payroll_adjustments_pkey PRIMARY KEY (id);


--
-- Name: payroll_line_items payroll_line_items_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_line_items
    ADD CONSTRAINT payroll_line_items_pkey PRIMARY KEY (id);


--
-- Name: payroll_periods payroll_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_periods
    ADD CONSTRAINT payroll_periods_pkey PRIMARY KEY (id);


--
-- Name: payroll_review_records payroll_review_records_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT payroll_review_records_pkey PRIMARY KEY (id);


--
-- Name: payroll_rules payroll_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_rules
    ADD CONSTRAINT payroll_rules_pkey PRIMARY KEY (id);


--
-- Name: policy_documents policy_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.policy_documents
    ADD CONSTRAINT policy_documents_pkey PRIMARY KEY (id);


--
-- Name: salary_records salary_records_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.salary_records
    ADD CONSTRAINT salary_records_pkey PRIMARY KEY (id);


--
-- Name: attendance_records uq_attendance_records_employee_date; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.attendance_records
    ADD CONSTRAINT uq_attendance_records_employee_date UNIQUE (employee_id, attendance_date);


--
-- Name: candidate_applications uq_candidate_applications_candidate_job; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_applications
    ADD CONSTRAINT uq_candidate_applications_candidate_job UNIQUE (candidate_id, job_id);


--
-- Name: candidates uq_candidates_candidate_no; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT uq_candidates_candidate_no UNIQUE (candidate_no);


--
-- Name: candidates uq_candidates_email; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT uq_candidates_email UNIQUE (email);


--
-- Name: candidates uq_candidates_phone; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidates
    ADD CONSTRAINT uq_candidates_phone UNIQUE (phone);


--
-- Name: employees uq_employees_email; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT uq_employees_email UNIQUE (email);


--
-- Name: employees uq_employees_employee_no; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT uq_employees_employee_no UNIQUE (employee_no);


--
-- Name: employees uq_employees_phone; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT uq_employees_phone UNIQUE (phone);


--
-- Name: employees uq_employees_user_id; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT uq_employees_user_id UNIQUE (user_id);


--
-- Name: interviewers uq_interviewers_employee_id; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviewers
    ADD CONSTRAINT uq_interviewers_employee_id UNIQUE (employee_id);


--
-- Name: jobs uq_jobs_job_code; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT uq_jobs_job_code UNIQUE (job_code);


--
-- Name: leave_balances uq_leave_balances_employee_year_type; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.leave_balances
    ADD CONSTRAINT uq_leave_balances_employee_year_type UNIQUE (employee_id, year, leave_type);


--
-- Name: meeting_rooms uq_meeting_rooms_room_code; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.meeting_rooms
    ADD CONSTRAINT uq_meeting_rooms_room_code UNIQUE (room_code);


--
-- Name: payroll_periods uq_payroll_periods_period_code; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_periods
    ADD CONSTRAINT uq_payroll_periods_period_code UNIQUE (period_code);


--
-- Name: payroll_review_records uq_payroll_review_records_employee_period; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT uq_payroll_review_records_employee_period UNIQUE (employee_id, payroll_period_id);


--
-- Name: payroll_rules uq_payroll_rules_rule_code; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_rules
    ADD CONSTRAINT uq_payroll_rules_rule_code UNIQUE (rule_code);


--
-- Name: policy_documents uq_policy_documents_document_code; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.policy_documents
    ADD CONSTRAINT uq_policy_documents_document_code UNIQUE (document_code);


--
-- Name: users uq_users_username; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uq_users_username UNIQUE (username);


--
-- Name: work_calendars uq_work_calendars_date; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.work_calendars
    ADD CONSTRAINT uq_work_calendars_date UNIQUE (calendar_date);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: work_calendars work_calendars_pkey; Type: CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.work_calendars
    ADD CONSTRAINT work_calendars_pkey PRIMARY KEY (id);


--
-- Name: ix_attendance_records_attendance_date; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_attendance_records_attendance_date ON public.attendance_records USING btree (attendance_date);


--
-- Name: ix_attendance_records_employee_date; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_attendance_records_employee_date ON public.attendance_records USING btree (employee_id, attendance_date);


--
-- Name: ix_attendance_records_status; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_attendance_records_status ON public.attendance_records USING btree (status);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_actor_created_at; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_audit_logs_actor_created_at ON public.audit_logs USING btree (actor_user_id, created_at);


--
-- Name: ix_audit_logs_target_employee_created_at; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_audit_logs_target_employee_created_at ON public.audit_logs USING btree (target_employee_id, created_at);


--
-- Name: ix_audit_logs_trace_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_audit_logs_trace_id ON public.audit_logs USING btree (trace_id);


--
-- Name: ix_candidate_applications_candidate_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_candidate_applications_candidate_id ON public.candidate_applications USING btree (candidate_id);


--
-- Name: ix_candidate_applications_job_stage; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_candidate_applications_job_stage ON public.candidate_applications USING btree (job_id, current_stage);


--
-- Name: ix_candidate_applications_score_total; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_candidate_applications_score_total ON public.candidate_applications USING btree (score_total);


--
-- Name: ix_candidates_available_from; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_candidates_available_from ON public.candidates USING btree (available_from);


--
-- Name: ix_candidates_source; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_candidates_source ON public.candidates USING btree (source);


--
-- Name: ix_employees_department; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_employees_department ON public.employees USING btree (department);


--
-- Name: ix_employees_employment_status; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_employees_employment_status ON public.employees USING btree (employment_status);


--
-- Name: ix_employees_manager_employee_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_employees_manager_employee_id ON public.employees USING btree (manager_employee_id);


--
-- Name: ix_interview_slots_candidate_time; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interview_slots_candidate_time ON public.interview_slots USING btree (candidate_id, start_at, end_at);


--
-- Name: ix_interview_slots_interviewer_time; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interview_slots_interviewer_time ON public.interview_slots USING btree (interviewer_id, start_at, end_at);


--
-- Name: ix_interview_slots_resource_type; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interview_slots_resource_type ON public.interview_slots USING btree (resource_type);


--
-- Name: ix_interview_slots_room_time; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interview_slots_room_time ON public.interview_slots USING btree (meeting_room_id, start_at, end_at);


--
-- Name: ix_interviewers_is_active; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interviewers_is_active ON public.interviewers USING btree (is_active);


--
-- Name: ix_interviews_application_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interviews_application_id ON public.interviews USING btree (application_id);


--
-- Name: ix_interviews_interviewer_time; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interviews_interviewer_time ON public.interviews USING btree (interviewer_id, start_at, end_at);


--
-- Name: ix_interviews_room_time; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interviews_room_time ON public.interviews USING btree (meeting_room_id, start_at, end_at);


--
-- Name: ix_interviews_status; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_interviews_status ON public.interviews USING btree (status);


--
-- Name: ix_jobs_department; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_jobs_department ON public.jobs USING btree (department);


--
-- Name: ix_jobs_owner_user_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_jobs_owner_user_id ON public.jobs USING btree (owner_user_id);


--
-- Name: ix_jobs_status; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_jobs_status ON public.jobs USING btree (status);


--
-- Name: ix_leave_balances_employee_year; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_leave_balances_employee_year ON public.leave_balances USING btree (employee_id, year);


--
-- Name: ix_meeting_rooms_is_active; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_meeting_rooms_is_active ON public.meeting_rooms USING btree (is_active);


--
-- Name: ix_notifications_notification_type; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_notifications_notification_type ON public.notifications USING btree (notification_type);


--
-- Name: ix_notifications_user_read_created_at; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_notifications_user_read_created_at ON public.notifications USING btree (user_id, is_read, created_at);


--
-- Name: ix_payroll_adjustments_created_by_user_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_adjustments_created_by_user_id ON public.payroll_adjustments USING btree (created_by_user_id);


--
-- Name: ix_payroll_adjustments_employee_period; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_adjustments_employee_period ON public.payroll_adjustments USING btree (employee_id, payroll_period_id);


--
-- Name: ix_payroll_adjustments_type; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_adjustments_type ON public.payroll_adjustments USING btree (adjustment_type);


--
-- Name: ix_payroll_line_items_payroll_rule_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_line_items_payroll_rule_id ON public.payroll_line_items USING btree (payroll_rule_id);


--
-- Name: ix_payroll_line_items_review_record_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_line_items_review_record_id ON public.payroll_line_items USING btree (payroll_review_record_id);


--
-- Name: ix_payroll_line_items_source_type; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_line_items_source_type ON public.payroll_line_items USING btree (source_type);


--
-- Name: ix_payroll_periods_status; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_periods_status ON public.payroll_periods USING btree (status);


--
-- Name: ix_payroll_review_records_confirmed_by_user_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_review_records_confirmed_by_user_id ON public.payroll_review_records USING btree (confirmed_by_user_id);


--
-- Name: ix_payroll_review_records_employee_period; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_review_records_employee_period ON public.payroll_review_records USING btree (employee_id, payroll_period_id);


--
-- Name: ix_payroll_review_records_generated_by_user_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_review_records_generated_by_user_id ON public.payroll_review_records USING btree (generated_by_user_id);


--
-- Name: ix_payroll_review_records_status; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_review_records_status ON public.payroll_review_records USING btree (status);


--
-- Name: ix_payroll_rules_applies_to; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_rules_applies_to ON public.payroll_rules USING btree (applies_to);


--
-- Name: ix_payroll_rules_direction; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_rules_direction ON public.payroll_rules USING btree (direction);


--
-- Name: ix_payroll_rules_is_active; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_payroll_rules_is_active ON public.payroll_rules USING btree (is_active);


--
-- Name: ix_pipeline_records_application_created_at; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_pipeline_records_application_created_at ON public.candidate_pipeline_records USING btree (application_id, created_at);


--
-- Name: ix_pipeline_records_changed_by_user_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_pipeline_records_changed_by_user_id ON public.candidate_pipeline_records USING btree (changed_by_user_id);


--
-- Name: ix_policy_documents_category; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_policy_documents_category ON public.policy_documents USING btree (category);


--
-- Name: ix_policy_documents_is_active; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_policy_documents_is_active ON public.policy_documents USING btree (is_active);


--
-- Name: ix_salary_records_created_by_user_id; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_salary_records_created_by_user_id ON public.salary_records USING btree (created_by_user_id);


--
-- Name: ix_salary_records_employee_effective_from; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_salary_records_employee_effective_from ON public.salary_records USING btree (employee_id, effective_from);


--
-- Name: ix_users_is_active; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_users_is_active ON public.users USING btree (is_active);


--
-- Name: ix_users_role; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_users_role ON public.users USING btree (role);


--
-- Name: ix_work_calendars_is_workday; Type: INDEX; Schema: public; Owner: talentflow
--

CREATE INDEX ix_work_calendars_is_workday ON public.work_calendars USING btree (is_workday);


--
-- Name: attendance_records attendance_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.attendance_records
    ADD CONSTRAINT attendance_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: attendance_records attendance_records_leave_balance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.attendance_records
    ADD CONSTRAINT attendance_records_leave_balance_id_fkey FOREIGN KEY (leave_balance_id) REFERENCES public.leave_balances(id) ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_actor_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_actor_user_id_fkey FOREIGN KEY (actor_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_target_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_target_employee_id_fkey FOREIGN KEY (target_employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: candidate_applications candidate_applications_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_applications
    ADD CONSTRAINT candidate_applications_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id) ON DELETE CASCADE;


--
-- Name: candidate_applications candidate_applications_job_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_applications
    ADD CONSTRAINT candidate_applications_job_id_fkey FOREIGN KEY (job_id) REFERENCES public.jobs(id) ON DELETE CASCADE;


--
-- Name: candidate_pipeline_records candidate_pipeline_records_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_pipeline_records
    ADD CONSTRAINT candidate_pipeline_records_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.candidate_applications(id) ON DELETE CASCADE;


--
-- Name: candidate_pipeline_records candidate_pipeline_records_changed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.candidate_pipeline_records
    ADD CONSTRAINT candidate_pipeline_records_changed_by_user_id_fkey FOREIGN KEY (changed_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: employees employees_manager_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_manager_employee_id_fkey FOREIGN KEY (manager_employee_id) REFERENCES public.employees(id) ON DELETE SET NULL;


--
-- Name: employees employees_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: interview_slots interview_slots_candidate_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interview_slots
    ADD CONSTRAINT interview_slots_candidate_id_fkey FOREIGN KEY (candidate_id) REFERENCES public.candidates(id) ON DELETE CASCADE;


--
-- Name: interview_slots interview_slots_interviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interview_slots
    ADD CONSTRAINT interview_slots_interviewer_id_fkey FOREIGN KEY (interviewer_id) REFERENCES public.interviewers(id) ON DELETE CASCADE;


--
-- Name: interview_slots interview_slots_meeting_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interview_slots
    ADD CONSTRAINT interview_slots_meeting_room_id_fkey FOREIGN KEY (meeting_room_id) REFERENCES public.meeting_rooms(id) ON DELETE CASCADE;


--
-- Name: interviewers interviewers_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviewers
    ADD CONSTRAINT interviewers_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: interviews interviews_application_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_application_id_fkey FOREIGN KEY (application_id) REFERENCES public.candidate_applications(id) ON DELETE CASCADE;


--
-- Name: interviews interviews_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: interviews interviews_interviewer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_interviewer_id_fkey FOREIGN KEY (interviewer_id) REFERENCES public.interviewers(id) ON DELETE RESTRICT;


--
-- Name: interviews interviews_meeting_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_meeting_room_id_fkey FOREIGN KEY (meeting_room_id) REFERENCES public.meeting_rooms(id) ON DELETE RESTRICT;


--
-- Name: jobs jobs_owner_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.jobs
    ADD CONSTRAINT jobs_owner_user_id_fkey FOREIGN KEY (owner_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: leave_balances leave_balances_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.leave_balances
    ADD CONSTRAINT leave_balances_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: payroll_adjustments payroll_adjustments_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_adjustments
    ADD CONSTRAINT payroll_adjustments_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: payroll_adjustments payroll_adjustments_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_adjustments
    ADD CONSTRAINT payroll_adjustments_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: payroll_adjustments payroll_adjustments_payroll_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_adjustments
    ADD CONSTRAINT payroll_adjustments_payroll_period_id_fkey FOREIGN KEY (payroll_period_id) REFERENCES public.payroll_periods(id) ON DELETE CASCADE;


--
-- Name: payroll_line_items payroll_line_items_payroll_review_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_line_items
    ADD CONSTRAINT payroll_line_items_payroll_review_record_id_fkey FOREIGN KEY (payroll_review_record_id) REFERENCES public.payroll_review_records(id) ON DELETE CASCADE;


--
-- Name: payroll_line_items payroll_line_items_payroll_rule_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_line_items
    ADD CONSTRAINT payroll_line_items_payroll_rule_id_fkey FOREIGN KEY (payroll_rule_id) REFERENCES public.payroll_rules(id) ON DELETE SET NULL;


--
-- Name: payroll_review_records payroll_review_records_confirmed_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT payroll_review_records_confirmed_by_user_id_fkey FOREIGN KEY (confirmed_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: payroll_review_records payroll_review_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT payroll_review_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- Name: payroll_review_records payroll_review_records_generated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT payroll_review_records_generated_by_user_id_fkey FOREIGN KEY (generated_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: payroll_review_records payroll_review_records_payroll_period_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT payroll_review_records_payroll_period_id_fkey FOREIGN KEY (payroll_period_id) REFERENCES public.payroll_periods(id) ON DELETE CASCADE;


--
-- Name: payroll_review_records payroll_review_records_salary_record_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.payroll_review_records
    ADD CONSTRAINT payroll_review_records_salary_record_id_fkey FOREIGN KEY (salary_record_id) REFERENCES public.salary_records(id) ON DELETE SET NULL;


--
-- Name: salary_records salary_records_created_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.salary_records
    ADD CONSTRAINT salary_records_created_by_user_id_fkey FOREIGN KEY (created_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: salary_records salary_records_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: talentflow
--

ALTER TABLE ONLY public.salary_records
    ADD CONSTRAINT salary_records_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict W2PQ0DcGixoT7pRtLZqdfT0Lpjq2jGuZFY2gVOtcaiBhJjC506rZtqfBSjla1Nk


