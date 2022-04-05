import os
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
import xml.etree.ElementTree as ET
import pickle
from django.conf import settings

class ApiViewGet(APIView):
    def get(self, *args, **kwargs):

        def map_function(StartLL, EndLL):
            RouteNodeLL = []
            route = requests.get(f'http://router.project-osrm.org/route/v1/driving/{StartLL};{EndLL}?alternatives=false&annotations=nodes')
            routejson = route.json()
            route_nodes = routejson['routes'][0]['legs'][0]['annotation']['nodes']

            if len(route_nodes) > 50 :
                x = len(route_nodes) / 49
                x = round(x)

            new_nodes = []
            c = 0
            while c < len(route_nodes):
                new_nodes.append(route_nodes[c])
                c += x

            for node in new_nodes:
                response_xml = requests.get(f'https://api.openstreetmap.org/api/0.6/node/{node}')
                response_xml_as_string = response_xml.content
                responseXml = ET.fromstring(response_xml_as_string)
                for child in responseXml.iter('node'):
                    RouteNodeLL.append((float(child.attrib['lat']), float(child.attrib['lon'])))

            return(RouteNodeLL)
        
        def call_model(lat_list, long_list) :
            models_folder = settings.BASE_DIR / 'map'
            file_path = os.path.join(models_folder, os.path.basename('model.pkl'))
            kmeans = pickle.load(open(file_path, 'rb'))

            lats = lat_list
            longs = long_list
            predictions = []

            for lat, long in zip(lats, longs) :
                prediction = kmeans.predict([[lat,long]])[0]
                if prediction not in predictions :
                    predictions.append(prediction)

            return(predictions)

        # -111.672670,40.240383/-111.645681,40.248471/
        StartLL = kwargs['coor1']
        EndLL = kwargs['coor2']

        list = map_function(StartLL, EndLL)

        lats = []
        longs = []

        for entry in list :
            lats.append(entry[0])
            longs.append(entry[1])

        predictions = call_model(lats, longs)

        return Response(predictions)

class ApiView(APIView):
    def get(self, request, format=None):
        return Response('yeet')