import pytest
from pydantic import ValidationError

from kernellab.config.loader import KernellabConfig, load_config, validate_config


@pytest.mark.unit
class TestLoadConfig:
    def test_load_valid_config(self, sample_config):
        config = load_config(sample_config)
        assert config.name == "test-lab"
        assert config.version == 1
        assert config.provider == "fake"
        assert config.machine.cpus == 2
        assert config.kernel.version == "6.12"
        assert len(config.tests) == 1
        assert config.tests[0].name == "test-echo"

    def test_load_missing_config(self, tmp_dir):
        with pytest.raises(FileNotFoundError):
            load_config(str(tmp_dir / "nonexistent.yaml"))


@pytest.mark.unit
class TestValidateConfig:
    def test_validate_config_valid(self, sample_config):
        config = load_config(sample_config)
        errors = validate_config(config)
        assert errors == []

    def test_validate_config_invalid_cpus(self):
        with pytest.raises(ValidationError):
            KernellabConfig(
                name="test",
                machine={"cpus": 0},
            )

    def test_validate_config_missing_name(self):
        config = KernellabConfig(
            name="",
        )
        errors = validate_config(config)
        assert any("name" in e for e in errors)
