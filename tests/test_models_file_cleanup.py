import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, models

from adjango.models.mixins import FileCleanupMixin


class CleanupDefaultModel(FileCleanupMixin):
    file1 = models.FileField(upload_to='cleanup/', blank=True, null=True)
    image = models.ImageField(upload_to='cleanup/', blank=True, null=True)

    class Meta:
        app_label = 'test_file_cleanup'


class CleanupCustomModel(FileCleanupMixin):
    file1 = models.FileField(upload_to='cleanup/', blank=True, null=True)
    file2 = models.FileField(upload_to='cleanup/', blank=True, null=True)
    image = models.ImageField(upload_to='cleanup/', blank=True, null=True)

    FILE_CLEANUP = {
        '*': {'on_replace': True, 'on_delete': True},
        'file2': {'on_replace': False},
        'image': False,
    }

    class Meta:
        app_label = 'test_file_cleanup'


class CleanupDisabledModel(FileCleanupMixin):
    file1 = models.FileField(upload_to='cleanup/', blank=True, null=True)

    FILE_CLEANUP = False

    class Meta:
        app_label = 'test_file_cleanup'


class CleanupSelectiveModel(FileCleanupMixin):
    file1 = models.FileField(upload_to='cleanup/', blank=True, null=True)
    file2 = models.FileField(upload_to='cleanup/', blank=True, null=True)

    FILE_CLEANUP = {
        '*': False,
        'file2': True,
    }

    class Meta:
        app_label = 'test_file_cleanup'


def _upload(name: str, content: bytes = b'data') -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content)


@pytest.fixture(scope='module', autouse=True)
def _create_cleanup_tables(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(CleanupDefaultModel)
            schema_editor.create_model(CleanupCustomModel)
            schema_editor.create_model(CleanupDisabledModel)
            schema_editor.create_model(CleanupSelectiveModel)
    yield
    with django_db_blocker.unblock():
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(CleanupSelectiveModel)
            schema_editor.delete_model(CleanupDisabledModel)
            schema_editor.delete_model(CleanupCustomModel)
            schema_editor.delete_model(CleanupDefaultModel)


@pytest.fixture(autouse=True)
def _temp_media_root(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path


@pytest.mark.django_db(transaction=True)
def test_file_cleanup_default_replace_and_delete():
    obj = CleanupDefaultModel.objects.create(
        file1=_upload('old.txt'),
        image=_upload('old.jpg', b'jpeg'),
    )
    storage = obj._meta.get_field('file1').storage

    old_file1 = obj.file1.name
    old_image = obj.image.name
    assert storage.exists(old_file1)
    assert storage.exists(old_image)

    obj.file1 = _upload('new.txt')
    obj.save()
    new_file1 = obj.file1.name

    assert not storage.exists(old_file1)
    assert storage.exists(old_image)
    assert storage.exists(new_file1)

    obj.delete()

    assert not storage.exists(new_file1)
    assert not storage.exists(old_image)


@pytest.mark.django_db(transaction=True)
def test_file_cleanup_custom_field_overrides():
    obj = CleanupCustomModel.objects.create(
        file1=_upload('f1_old.txt'),
        file2=_upload('f2_old.txt'),
        image=_upload('img_old.jpg', b'jpeg'),
    )
    storage = obj._meta.get_field('file1').storage

    old_file1 = obj.file1.name
    old_file2 = obj.file2.name
    old_image = obj.image.name

    obj.file1 = _upload('f1_new.txt')
    obj.file2 = _upload('f2_new.txt')
    obj.image = _upload('img_new.jpg', b'jpeg')
    obj.save()

    new_file1 = obj.file1.name
    new_file2 = obj.file2.name
    new_image = obj.image.name

    assert not storage.exists(old_file1)     # default on_replace=True
    assert storage.exists(old_file2)         # override on_replace=False
    assert storage.exists(old_image)         # image cleanup disabled

    obj.delete()

    assert not storage.exists(new_file1)     # default on_delete=True
    assert not storage.exists(new_file2)     # inherited on_delete=True
    assert storage.exists(new_image)         # image cleanup disabled


@pytest.mark.django_db(transaction=True)
def test_file_cleanup_disabled_globally():
    obj = CleanupDisabledModel.objects.create(file1=_upload('disabled_old.txt'))
    storage = obj._meta.get_field('file1').storage
    old_file = obj.file1.name

    obj.file1 = _upload('disabled_new.txt')
    obj.save()
    new_file = obj.file1.name

    assert storage.exists(old_file)
    assert storage.exists(new_file)

    obj.delete()

    assert storage.exists(old_file)
    assert storage.exists(new_file)


@pytest.mark.django_db(transaction=True)
def test_file_cleanup_selective_enable_with_star_default():
    obj = CleanupSelectiveModel.objects.create(
        file1=_upload('sel_f1_old.txt'),
        file2=_upload('sel_f2_old.txt'),
    )
    storage = obj._meta.get_field('file1').storage

    old_file1 = obj.file1.name
    old_file2 = obj.file2.name

    obj.file1 = _upload('sel_f1_new.txt')
    obj.file2 = _upload('sel_f2_new.txt')
    obj.save()

    new_file1 = obj.file1.name
    new_file2 = obj.file2.name

    assert storage.exists(old_file1)         # '*'=False disables cleanup
    assert not storage.exists(old_file2)     # file2=True enables cleanup

    obj.delete()

    assert storage.exists(new_file1)         # disabled
    assert not storage.exists(new_file2)     # enabled
