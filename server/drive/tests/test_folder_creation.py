import pytest
from django.urls import reverse

from drive.models import Node, StorageUsage


@pytest.mark.django_db
def test_create_root_and_nested_folders(
    api_client,
    user,
):
    api_client.force_authenticate(user=user)

    url = reverse("create-folder")

    # --------------------
    # 1. CREATE ROOT FOLDER
    # --------------------
    payload_root = {
        "parent_id": None,
        "name": "Projects",
    }

    response_root = api_client.post(url, payload_root, format="json")
    assert response_root.status_code == 201

    root_data = response_root.data
    root_id = root_data["id"]

    root_node = Node.objects.get(id=root_id)

    assert root_node.name == "Projects"
    assert root_node.is_folder is True
    assert root_node.depth == 2  # treebeard root
    assert root_node.owner == user

    # --------------------
    # 2. CREATE FIRST CHILD FOLDER
    # --------------------
    payload_child_1 = {
        "parent_id": root_id,
        "name": "Backend",
    }

    response_child_1 = api_client.post(url, payload_child_1, format="json")
    assert response_child_1.status_code == 201

    child_1_data = response_child_1.data
    child_1 = Node.objects.get(id=child_1_data["id"])

    assert child_1.depth == root_node.depth + 1
    assert child_1.is_folder is True

    # --------------------
    # 3. CREATE SECOND CHILD (CONSECUTIVE CREATION)
    # --------------------
    payload_child_2 = {
        "parent_id": root_id,
        "name": "Frontend",
    }

    response_child_2 = api_client.post(url, payload_child_2, format="json")
    assert response_child_2.status_code == 201

    child_2_data = response_child_2.data
    child_2 = Node.objects.get(id=child_2_data["id"])

    assert child_2.depth == root_node.depth + 1
    assert child_2.is_folder is True

    # --------------------
    # 4. TREE INTEGRITY CHECKS
    # --------------------
    root_node.refresh_from_db()
    children = root_node.get_children()
    assert children.count() == 2

    child_names = {c.name for c in children}
    assert child_names == {"Backend", "Frontend"}

    # --------------------
    # 5. STORAGE USAGE SHOULD NOT CHANGE
    # --------------------
    usage = StorageUsage.objects.get(user=user)
    assert usage.used_bytes == 0


@pytest.mark.django_db
def test_same_folder_name_allowed_under_different_parents(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("create-folder")

    root1 = api_client.post(url, {"parent_id": None, "name": "A"}, format="json").data["id"]
    root2 = api_client.post(url, {"parent_id": None, "name": "B"}, format="json").data["id"]

    res1 = api_client.post(url, {"parent_id": root1, "name": "Docs"}, format="json")
    res2 = api_client.post(url, {"parent_id": root2, "name": "Docs"}, format="json")

    assert res1.status_code == 201
    assert res2.status_code == 201


@pytest.mark.django_db
def test_cannot_create_folder_under_file(api_client, user):
    api_client.force_authenticate(user=user)
    url = reverse("create-folder")

    file_node = Node.objects.create(
        name="testfile",
        owner=user,
        type=Node.NodeType.file,
        status=Node.NodeStatus.ACTIVE,
        depth=1
    )

    response = api_client.post(
        url,
        {"parent_id": file_node.id, "name": "Invalid"},
        format="json",
    )

    assert response.status_code == 400



