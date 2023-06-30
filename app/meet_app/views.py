from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django_filters import rest_framework as django_filters
from geopy.distance import geodesic
from rest_framework import filters
from rest_framework import generics, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Like
from .models import Participant, Match
from .serializers import ParticipantSerializer, ParticipantLoginSerializer


class CreateParticipantView(generics.CreateAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer




class MatchParticipantView(APIView):
    def post(self, request, id):
        try:
            participant = Participant.objects.get(id=id)
            current_user_email = request.user.email
            participant_email = participant.user.email

            if current_user_email == participant_email:
                return Response({'detail': 'You cannot match with yourself.'}, status=400)

            existing_match = Match.objects.filter(participant1__user__email=current_user_email,
                                                  participant2__user__email=participant_email)
            if existing_match.exists():
                return Response({'detail': 'Match already exists.'}, status=400)

            current_user = User.objects.get(email=current_user_email)
            participant_user = User.objects.get(email=participant_email)

            like, created = Like.objects.get_or_create(participant=participant, liked_by=current_user)

            if created:
                email_subject = f'Вы понравились {request.user.first_name}!'
                email_body = f'Почта участника: {participant_email}'

                return Response({'detail': 'Like created.'}, status=201)

            # Check for mutual like
            if Like.objects.filter(participant=participant, liked_by=current_user).exists():
                match = Match(participant1=participant_user, participant2=current_user)
                match.save()

                email_subject = f'Вы понравились {request.user.first_name}!'
                email_body = f'Почта участника: {participant_email}'

                return Response({'detail': f'Match created between {current_user_email} and {participant_email}.'},
                                status=201)

            return Response({'detail': 'No match.'}, status=200)

        except Participant.DoesNotExist:
            return Response({'detail': 'Participant not found.'}, status=404)
        except User.DoesNotExist:
            return Response({'detail': 'User not found.'}, status=404)


class ParticipantLoginView(APIView):
    def post(self, request):
        serializer = ParticipantLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                participant = Participant.objects.get(user__email=email)
            except Participant.DoesNotExist:
                return Response({'detail': 'Неверные учетные данные пользователя.'},
                                status=status.HTTP_401_UNAUTHORIZED)

            if check_password(password, participant.user.password):
                login(request, participant.user)
                return Response({'detail': 'Аутентификация прошла успешно.', 'token': request.session.session_key},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Неверные учетные данные пользователя.'},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParticipantFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Participant.GENDER_CHOICES)

    distance = django_filters.NumberFilter(method='filter_distance')

    def filter_distance(self, queryset, name, value):
        user = self.request.user.participant
        user_latitude = user.latitude
        user_longitude = user.longitude

        # Фильтрация участников по расстоянию
        distance_threshold = int(value)  # Значение фильтра расстояния
        queryset = queryset.filter(latitude__isnull=False,
                                   longitude__isnull=False)  # Фильтр для участников с известными координатами

        filtered_participants = []
        for participant in queryset:
            distance = self.calculate_distance(user_latitude, user_longitude, participant.latitude,
                                               participant.longitude)
            if distance <= distance_threshold:
                filtered_participants.append(participant)

        return self.queryset.model.objects.filter(pk__in=[participant.pk for participant in filtered_participants])

    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        point1 = (lat1, lon1)
        point2 = (lat2, lon2)
        distance = geodesic(point1, point2).kilometers
        return distance


class ParticipantListView(ListAPIView):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    filter_backends = [filters.OrderingFilter, django_filters.DjangoFilterBackend]
    filterset_class = ParticipantFilter
    ordering_fields = ['first_name', 'last_name']
