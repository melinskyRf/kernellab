import pytest

from kernellab.runtime.command_runner import CommandRunner
from kernellab.runtime.exceptions import CommandExecutionError, CommandTimeoutError


@pytest.mark.unit
class TestCommandRunner:
    def test_run_success(self):
        runner = CommandRunner()
        result = runner.run("echo", ["hello"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "hello"
        assert result.stderr == ""
        assert result.duration >= 0

    def test_run_failure(self):
        runner = CommandRunner()
        with pytest.raises(CommandExecutionError) as exc_info:
            runner.run("false", [])
        assert exc_info.value.exit_code != 0

    def test_run_failure_check_false(self):
        runner = CommandRunner()
        result = runner.run("false", [], check=False)
        assert result.exit_code != 0
        assert result.stdout == ""

    def test_run_timeout(self):
        runner = CommandRunner()
        with pytest.raises(CommandTimeoutError) as exc_info:
            runner.run("sleep", ["10"], timeout=1)
        assert exc_info.value.timeout == 1

    def test_run_stderr(self):
        runner = CommandRunner()
        result = runner.run("bash", ["-c", "echo error >&2"], check=False)
        assert "error" in result.stderr

    def test_run_nonexistent_executable(self):
        runner = CommandRunner()
        with pytest.raises(CommandExecutionError):
            runner.run("/nonexistent/binary", [])
