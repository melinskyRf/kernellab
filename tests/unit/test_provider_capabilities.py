import pytest

from kernellab.providers.base import ProviderCapabilities


@pytest.mark.unit
class TestProviderCapabilities:
    def test_capabilities_all_true(self):
        caps = ProviderCapabilities(
            create=True, start=True, stop=True, destroy=True,
            serial=True, snapshots=True, guest_exec=True,
        )
        assert caps.all is True

    def test_capabilities_all_false(self):
        caps = ProviderCapabilities(
            create=False, start=False, stop=False, destroy=False,
            serial=False, snapshots=False, guest_exec=False,
        )
        assert caps.all is False

    def test_capabilities_mixed(self):
        caps = ProviderCapabilities(
            create=True, start=True, stop=True, destroy=True,
            serial=False, snapshots=False, guest_exec=False,
        )
        assert caps.all is False

    @pytest.mark.real_virtualization
    def test_virtualbox_capabilities(self):
        from kernellab.providers.virtualbox import VirtualBoxProvider

        provider = VirtualBoxProvider()
        caps = provider.capabilities()
        assert caps.serial is False
        assert caps.snapshots is True
        assert caps.guest_exec is False
