from django.core.management.base import BaseCommand
from core.models import ServiceRequest, Volunteer
from datetime import date, timedelta, time
import random

class Command(BaseCommand):
    help = 'Seed demo data for MVP'

    def handle(self, *args, **opts):
        ServiceRequest.objects.all().delete()
        Volunteer.objects.all().delete()

        volunteers = [
            ('أبو محمد','riyadh',['electric']),
            ('نواف','jeddah',['move','senior']),
            ('خالد','dammam',['health']),
            ('سلمان','riyadh',['move','electric']),
            ('عبدالله','makkah',['senior','health']),
        ]
        for n,c,s in volunteers:
            Volunteer.objects.create(name=n, city=c, skills=s)

        demo = [
            dict(name="أم خالد", phone="0551234567", city="riyadh", type="electric", desc="تركيب لمبتين في الصالة",  date=date.today(),     time=time(18,0), status="pending"),
            dict(name="أبو محمد", phone="0552345678", city="jeddah", type="move",    desc="نقل كرسيين وطاولة",      date=date.today(),     time=time(20,0), status="accepted"),
            dict(name="أبو فهد",  phone="0553456789", city="dammam", type="health",  desc="توصيل للمستشفى صباحًا", date=date.today()+timedelta(days=1), time=time(9,0), status="pending"),
            dict(name="أم عمر",   phone="0554567890", city="makkah", type="senior",  desc="مساعدة في التسوق",      date=date.today()-timedelta(days=1), time=time(17,0), status="inprogress"),
            dict(name="أم ياسر",  phone="0555678901", city="madinah",type="other",   desc="تنظيف بسيط للشرفة",      date=date.today()-timedelta(days=2), time=time(19,30), status="done"),
        ]

        CITY_GEO = {
            'riyadh':  (24.7136, 46.6753),
            'jeddah':  (21.4858, 39.1925),
            'dammam':  (26.4207, 50.0888),
            'madinah': (24.4709, 39.6122),
            'makkah':  (21.3891, 39.8579),
        }

        for d in demo:
            lat,lng = CITY_GEO.get(d['city'], (24.7,46.6))
            lat += (random.random()-.5)*0.05
            lng += (random.random()-.5)*0.05
            ServiceRequest.objects.create(lat=lat, lng=lng, **d)

        self.stdout.write(self.style.SUCCESS('✓ Seeded demo data successfully'))
