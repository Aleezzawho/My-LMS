-- The SQL judge connects as `sqljudge` but every submission runs as `sub_runner`.
-- No superuser, no file access, no extensions, no dblink.
CREATE ROLE sub_runner LOGIN PASSWORD 'CHANGE_ME_AT_PROVISIONING'
  NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS
  CONNECTION LIMIT 5;

REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO sub_runner;

ALTER ROLE sub_runner SET statement_timeout = '5s';
ALTER ROLE sub_runner SET idle_in_transaction_session_timeout = '10s';
ALTER ROLE sub_runner SET work_mem = '16MB';
ALTER ROLE sub_runner SET search_path = public;
