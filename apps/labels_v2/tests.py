from django.test import TestCase
from django.urls import reverse

from apps import common_prepare
from .models import Label, LabelFollow


class LabelViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.path = reverse("labels_v2:root")
        self.data = {"name": "标签", "intro": "好", "avatar": "/pub/3.png"}

    def test_no_login(self):
        response = self.client.post(self.path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_name(self):
        data = self.data.copy()
        data.pop("name")
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_name_is_none(self):
        data = self.data.copy()
        data["name"] = None
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_empty_name(self):
        data = self.data.copy()
        data["name"] = ""
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_bad_name(self):
        response = self.client.post(self.path, {"name": "<", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        response = self.client.post(self.path, {"name": ">", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)
        response = self.client.post(self.path, {"name": "&", "intro": "好", "avatar": "/pub/3.png"}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_name_exist(self):
        Label.objects.create(**self.data)
        response = self.client.post(self.path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_intro(self):
        data = self.data.copy()
        data.pop("intro")
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["intro"])

    def test_intro_is_none(self):
        data = self.data.copy()
        data["intro"] = None
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["intro"])

    def test_empty_intro(self):
        data = self.data.copy()
        data["intro"] = ""
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["intro"])

    def test_no_avatar(self):
        data = self.data.copy()
        data.pop("avatar")
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["avatar"])

    def test_avatar_is_none(self):
        data = self.data.copy()
        data["avatar"] = None
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["avatar"])

    def test_empty_avatar(self):
        data = self.data.copy()
        data["avatar"] = ""
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertIsNone(data["data"]["avatar"])

    def test_bad_avatar(self):
        data = self.data.copy()
        data["avatar"] = "afd/1.pn"
        response = self.client.post(self.path, data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)


class OneLabelViewDeleteTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(**{"name": "标签", "intro": "好", "avatar": "/pub/3.png"})

    def test_label_not_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk + 1})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_label_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class OneLabelViewPutTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.old_data = {"name": "标签", "intro": "好", "avatar": "/pub/3.png"}
        self.label = Label.objects.create(**self.old_data)
        self.data = {"name": "新标签", "intro": "新说明", "avatar": "/pub/12.jpg"}

    def test_no_login(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        response = self.client.put(path, self.data)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_label_not_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk + 1})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_label_exist(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        response = self.client.put(path, self.data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(data["data"]["name"], self.data["name"])
        self.assertEqual(data["data"]["intro"], self.data["intro"])
        self.assertEqual(data["data"]["avatar"], self.data["avatar"])

    def test_label_name_unchanged(self):
        path = reverse("labels_v2:one_label", kwargs={"label_id": self.label.pk})
        data = self.data.copy()
        data["name"] = self.old_data["name"]
        response = self.client.put(path, data, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class ChildLabelViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label1 = Label.objects.create(name="标签1")
        self.label2 = Label.objects.create(name="标签2")
        self.path = reverse("labels_v2:child", kwargs={"label_id": self.label1.pk})

    def test_no_login(self):
        response = self.client.post(self.path, {"id": self.label2.pk})
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_parent(self):
        path = reverse("labels_v2:child", kwargs={"label_id": self.label1.pk + self.label2.pk})
        response = self.client.post(path, {"id": self.label2.pk}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_child(self):
        response = self.client.post(self.path, {"id": self.label2.pk + self.label1.pk}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_child_is_self(self):
        response = self.client.post(self.path, {"id": self.label1.pk}, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_ok(self):
        response = self.client.post(self.path, {"id": self.label2.pk}, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class ChildLabelViewDeleteTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.parent = Label.objects.create(name="标签1")
        self.child = Label.objects.create(name="标签2")
        self.path = reverse("labels_v2:child", kwargs={"label_id": self.parent.pk})

    def test_no_login(self):
        response = self.client.delete(self.path + "?id=" + str(self.child.pk))
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_no_parent(self):
        path = reverse("labels_v2:child", kwargs={"label_id": self.parent.pk + self.child.pk})
        path = path + "?id=" + str(self.child.pk)
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)

    def test_no_child(self):
        path = self.path + "?id=" + str(self.child.pk + self.parent.pk)
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)


class LabelFollowViewPostTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.path = reverse("labels_v2:follow", kwargs={"label_id": self.label.pk})

    def test_no_login(self):
        response = self.client.post(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_label_not_exist(self):
        path = reverse("labels_v2:follow", kwargs={"label_id": self.label.pk + 1})
        response = self.client.post(path, **self.headers)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_follow_only_once(self):
        response = self.client.post(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        response = self.client.post(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(self.label.followers.count(), 1)


class LabelFollowViewDeleteTest(TestCase):
    def setUp(self):
        common_prepare(self)
        self.label = Label.objects.create(name="标签1")
        self.path = reverse("labels_v2:follow", kwargs={"label_id": self.label.pk})
        user = self.users["zhang"]
        LabelFollow.objects.create(user=user, label=self.label)

    def test_no_login(self):
        response = self.client.delete(self.path)
        data = response.json()
        self.assertNotEqual(data["code"], 0)

    def test_label_followed(self):
        self.assertEqual(LabelFollow.objects.count(), 1)
        response = self.client.delete(self.path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(LabelFollow.objects.count(), 0)

    def test_label_not_followed(self):
        self.assertEqual(LabelFollow.objects.count(), 1)
        path = reverse("labels_v2:follow", kwargs={"label_id": self.label.pk + 1})
        response = self.client.delete(path, **self.headers)
        data = response.json()
        self.assertEqual(data["code"], 0)
        self.assertEqual(LabelFollow.objects.count(), 1)
