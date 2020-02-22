from rest_framework import serializers


class FavoritesValidator(serializers.Serializer):
    uid = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    content = serializers.CharField(allow_null=True, allow_blank=True)
    STATUS = (('public', 'public'), ('private', 'private'))
    status = serializers.ChoiceField(choices=STATUS)


class BookMarksUpdateValidator(serializers.Serializer):
    uid = serializers.CharField(required=True)
    bm_id = serializers.IntegerField(required=True)
    title = serializers.CharField(required=True)
    content = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    STATUS = (('public', 'public'), ('private', 'private'))
    status = serializers.ChoiceField(choices=STATUS)