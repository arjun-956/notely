from django.shortcuts import render

# generic create api view

from rest_framework import generics

from notes.serializers import UserSerializer,TaskSerializer

from notes.models import User,Task

from rest_framework.response import Response

from rest_framework import permissions,authentication

from notes.permissions import OwnerOnly

from rest_framework.views import APIView

from django.db.models import Count

class UserCreationView(generics.CreateAPIView):

    serializer_class=UserSerializer

class TaskListCreateView(generics.ListCreateAPIView):

    serializer_class=TaskSerializer

    queryset=Task.objects.all()    

    #authentication_classes=[authentication.BasicAuthentication]
    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]
    

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    # def list(self,request,*args,**kwargs):

    #     qs=Task.objects.filter(owner=request.user)

    #     serializer_instance=TaskSerializer(qs,many=True)       ==== optional

    #     return Response(data=serializer_instance.data)

    def get_queryset(self):

        qs=Task.objects.filter(owner=self.request.user)

        if "category" in self.request.query_params:
                                                                         #optional ; http://127.0.0.1:8000/api/tasks?category=business
            category_value=self.request.query_params.get("category")

            qs=qs.filter(category=category_value)

        return qs


   
    

class TaskRetriveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    queryset=Task.objects.all()

    serializer_class=TaskSerializer

    #authentication_classes=[authentication.BasicAuthentication]
    
    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[OwnerOnly]

class TaskSummaryApiView(APIView):

    #authentication_classes=[authentication.BasicAuthentication]
    
    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]


    def get(self,request,*args,**kwargs):

      
        qs=Task.objects.filter(owner=request.user)

        category_summary=qs.values("category").annotate(count=Count("category"))

        status_summary=qs.values("status").annotate(count=Count("status"))

        priority_summary=qs.values('priority').annotate(count=Count("priority"))

        total_count=qs.count()

        context={

            "category_summary":category_summary,

            "status_summary":status_summary,

            "priority_summary":priority_summary,

            "total_count":total_count

        }

        return Response(data=context)
    

class CategoryListView(APIView):

    def get(self,request,*args,**kwargs):

        categories=Task.category_choices

        """
         (
        ("business","business"),

        ("personal","personal")
        
        )
    
        """

        cat=[{cat for tp in categories for cat in tp}]

        return Response(data=cat)