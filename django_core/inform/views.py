from rest_framework import views, response, status

from .serializers import InformationSerializer
from .models import Information

from api.models import CustomUser
from api.serializers import UserSerializer


class AnonInformation(views.APIView):
    def post(self, request):
        weight = int(request.data['weight']) * 10
        height = int(request.data['height']) * 6.25
        age = int(request.data['age']) * 5
        gender = self.get_gender(request.data['gender'])
        activity = request.data['activity']
        target = request.data['target']
        allergen = request.data['allergen']

        calorie = self.get_calorie()
        protein = self.get_protein(calorie)
        fats = self.get_fats(calorie)
        carbohydrates = self.get_carbohydrates(calorie)

        response_info = response.Response()

        response_info.set_cookie(key='weight', value=weight, httponly=True)
        response_info.set_cookie(key='height', value=height, httponly=True)
        response_info.set_cookie(key='age', value=age, httponly=True)
        response_info.set_cookie(key='gender', value=gender, httponly=True)
        response_info.set_cookie(key='activity', value=activity, httponly=True)
        response_info.set_cookie(key='target', value=target, httponly=True)
        response_info.set_cookie(key='calorie', value=calorie, httponly=True)
        response_info.set_cookie(key='protein', value=protein, httponly=True)
        response_info.set_cookie(key='fats', value=fats, httponly=True)
        response_info.set_cookie(key='carbohydrates', value=carbohydrates, httponly=True)
        response_info.set_cookie(key='allergen', value=allergen, httponly=True)

        response_info.data = {
            'success': 'data saved'
        }

        response_info.status_code = status.HTTP_201_CREATED

        return response_info

    def get_calorie(self):
        weight = int(self.request.data['weight']) * 10
        height = int(self.request.data['height']) * 6.25
        age = int(self.request.data['age']) * 5
        gender = self.get_gender(self.request.data['gender'])
        activity = self.get_activity(self.request.data['activity'])
        target = self.request.data['target']
        calorie = (weight + height - age + gender) * activity

        if target == 'Похудеть':
            return calorie - ((weight + height - age + gender) * activity) * 0.1
        elif target == 'Набрать вес':
            return calorie + ((weight + height - age + gender) * activity) * 0.1
        elif target == 'Сохранение веса':
            return calorie
        else:
            return response.Response({'Message': 'error'})

    @staticmethod
    def get_gender(gender):

        if gender == 'М':
            gender = 'M'
        elif gender == 'Ж':
            gender = 'F'

        gender_data = {
            'M': 5,
            'F': -161
        }

        return gender_data[gender]

    @staticmethod
    def get_activity(activity):

        activity_data = {
            'Минимум': 1.2,
            'Низкая': 1.375,
            'Средняя': 1.55,
            'Высокая': 1.725,
            'Предельная': 1.9
        }

        return activity_data[activity]

    @staticmethod
    def get_protein(calorie):
        return round((calorie * 0.3) / 4, 2)

    @staticmethod
    def get_fats(calorie):
        return round((calorie * 0.3) / 9, 2)

    @staticmethod
    def get_carbohydrates(calorie):
        return round((calorie * 0.4) / 4, 2)


class InformationView(views.APIView):
    def post(self, request):
        # TODO: на защите поменять!!!
        # request.data['user'] = request.user.pk
        request.data['user'] = 1

        request.data['calorie'] = calorie = self.get_calorie()
        request.data['protein'] = self.get_protein(calorie)
        request.data['fats'] = self.get_fats(calorie)
        request.data['carbohydrates'] = self.get_carbohydrates(calorie)

        serializer = InformationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return response.Response(data={'Success': 'Information created',
                                       'Data': serializer.data},
                                 status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):

        request.data['calorie'] = calorie = self.get_calorie()
        request.data['protein'] = self.get_protein(calorie)
        request.data['fats'] = self.get_fats(calorie)
        request.data['carbohydrates'] = self.get_carbohydrates(calorie)

        instance = Information.objects.get(pk=request.data['id'])

        serializer = InformationSerializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data={'Success': 'Information changed',
                                       'Data': serializer.data},
                                 status=status.HTTP_201_CREATED)

    def get_calorie(self):
        gender = self.get_gender(self.request.data['gender'])
        age = self.request.data['age']
        weight = self.request.data['weight']
        height = self.request.data['height']
        activity = self.get_activity(self.request.data['activity'])
        target = self.request.data['target']
        calorie = (gender - int(age) * 5 + int(weight) * 10 + int(height) * 6.25) * activity

        if target == 'Похудеть':
            calorie -= ((gender - int(age) * 5 + int(weight) * 10 + int(height) * 6.25) * activity) * 0.1
        elif target == 'Набор веса':
            calorie += ((gender - int(age) * 5 + int(weight) * 10 + int(height) * 6.25) * activity) * 0.1
        elif target == 'Сохранение веса':
            return calorie

        return calorie

    @staticmethod
    def get_gender(gender):

        gender_data = {
            'М': 5,
            'Ж': -161
        }

        return gender_data[gender]

    @staticmethod
    def get_activity(activity):

        activity_data = {
            'Минимальная': 1.2,
            'Низкая': 1.375,
            'Средняя': 1.55,
            'Высокая': 1.725,
            'Предельная': 1.9
        }

        return activity_data[activity]

    @staticmethod
    def get_protein(data):
        return round((data * 0.3) / 4, 2)

    @staticmethod
    def get_fats(data):
        return round((data * 0.3) / 9, 2)

    @staticmethod
    def get_carbohydrates(data):
        return round((data * 0.4) / 4, 2)


class GetDataView(views.APIView):
    def get(self, request):
        user_data = CustomUser.objects.filter().first()
        user_serializer = UserSerializer(user_data).data

        information_data = Information.objects.filter().first()
        information_serializer = InformationSerializer(information_data).data
        return response.Response({'user': user_serializer,
                                  'anketa': information_serializer})
