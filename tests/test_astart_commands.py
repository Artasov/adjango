from django.core.management import call_command

from adjango.management.commands.astartproject import Command as StartProjectCommand
from adjango.management.commands.astartup import Command as StartupCommand


def test_astartproject_creates_structure(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    call_command(StartProjectCommand(), 'sample')

    project_dir = tmp_path / 'sample'
    assert (project_dir / 'manage.py').exists()
    settings_path = project_dir / 'config' / 'settings.py'
    content = settings_path.read_text()
    assert "'apps.core'" in content
    assert "ROOT_URLCONF = 'apps.core.roads.root'" in content
    assert (project_dir / 'apps' / 'core' / 'roads' / 'root.py').exists()


def test_astartup_creates_app(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    call_command(StartProjectCommand(), 'sample')
    project_dir = tmp_path / 'sample'
    monkeypatch.chdir(project_dir)

    call_command(StartupCommand(), 'blog')

    blog_dir = project_dir / 'apps' / 'blog'
    expected = {
        'controllers/base.py',
        'admin/base.py',
        'exceptions/base.py',
        'models/base.py',
        'roads/api.py',
        'serializers/base.py',
        'services/base.py',
        'tests/base.py',
    }
    for path in expected:
        assert (blog_dir / path).exists()

    settings_path = project_dir / 'config' / 'settings.py'
    assert "'apps.blog'" in settings_path.read_text()
