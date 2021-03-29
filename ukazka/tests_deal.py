import responses
from config.models import Deal, Person, DealHasPerson, PersonHasPerson
from django.contrib.auth.models import Permission, User
from django.test import Client, TestCase
from faker import Faker
from jana.tests.factories import (
    DealFactory,
    DealHasPersonFactory,
    PersonFOFactory,
    PersonPOFactory,
    PersonFOPFactory, 
    PersonHasPersonFactory,
)

fake = Faker()
client = Client()

class TestRoleOsobyDealIU(TestCase):
    def setUp(self):
        # Login and rules setup
        self.user = User.objects.create_user(username="testovaciuser", password="testovaciheslo")
        my_secret = "MYTESTSECRETCODE"
        UserSecretCode.objects.create(user_id=self.user.id, secret_key=my_secret)
        client.post("/login/", {"username": "testovaciuser", "password": "testovaciheslo"})
        self.user.user_permissions.add(Permission.objects.get(codename="view_deal"))

        # SetUp popisujici investicni uver, kde prvni vlkadame fizickou osobu do systemu
        self.deal_id = 5717
        deal = DealFactory(id=self.deal_id, deal_typ="IU", hodnota=1996719745, dny_po_splatnosti=17,
                           zustatek_jistiny=1.550, datum_od="2019-02-06", datum_do="2023-06-13",
                           datum_zesplatneni="2023-08-11", owner='Květoslav Překližka', poslat_na_katastr=1,
                           poslat_vyzvu=1, stage="DPS 15-34", vyzva_moznost=None)

        self.alice_person_id = 111
        self.alice_fo_id = 11111
        self.alice_fop_id = 22222
        alice = PersonFOFactory(person_id=self.alice_person_id, id=self.alice_fo_id)
        podnikatel_alice = PersonFOPFactory(person_id=self.alice_person_id, id=self.alice_fop_id)
        PersonHasPersonFactory(person_fk=podnikatel_alice, fo_fk=alice, vztah="fop")
        DealHasPersonFactory(deal_fk=deal, person_fk=alice)
        DealHasPersonFactory(deal_fk=deal, person_fk=podnikatel_alice)

        self.sem_po_id = 55555
        sem = PersonPOFactory(id=self.sem_po_id)
        DealHasPersonFactory(deal_fk=deal, person_fk=sem)

    def test_fo_iu(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.alice_fo_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.alice_fo_id)
        self.assertEqual(deal_has_peson_query.zadatel, 0)
        self.assertEqual(deal_has_peson_query.zastavce, 1)
        self.assertEqual(deal_has_peson_query.spoludluznik, 0)
        self.assertEqual(deal_has_peson_query.najemce, 0)
        self.assertEqual(deal_has_peson_query.prodavajici, 0)
        self.assertEqual(deal_has_peson_query.rucitel, 1)
        self.assertEqual(deal_has_peson_query.pristupitel, 1)

    def test_fop_iu(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.alice_fop_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.alice_fop_id)
        self.assertEqual(deal_has_peson_query.zadatel, 1)
        self.assertEqual(deal_has_peson_query.zastavce, 0)
        self.assertEqual(deal_has_peson_query.spoludluznik, 1)
        self.assertEqual(deal_has_peson_query.najemce, 0)
        self.assertEqual(deal_has_peson_query.prodavajici, 0)
        self.assertEqual(deal_has_peson_query.rucitel, 1)
        self.assertEqual(deal_has_peson_query.pristupitel, 1)

    def test_po_iu(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.sem_po_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.sem_po_id)
        self.assertEqual(deal_has_peson_query.zadatel, 1)
        self.assertEqual(deal_has_peson_query.zastavce, 1)
        self.assertEqual(deal_has_peson_query.spoludluznik, 1)
        self.assertEqual(deal_has_peson_query.najemce, 0)
        self.assertEqual(deal_has_peson_query.prodavajici, 0)
        self.assertEqual(deal_has_peson_query.rucitel, 1)
        self.assertEqual(deal_has_peson_query.pristupitel, 1)


class TestRoleOsobyDealSU(TestCase):
    def setUp(self):
        # Login and rules setup
        self.user = User.objects.create_user(username="testovaciuser", password="testovaciheslo")
        my_secret = "MYTESTSECRETCODE"
        UserSecretCode.objects.create(user_id=self.user.id, secret_key=my_secret)
        client.post("/login/", {"username": "testovaciuser", "password": "testovaciheslo"})
        self.user.user_permissions.add(Permission.objects.get(codename="view_deal"))

        # SetUp popisujici investicni uver, kde prvni vlkadame fizickou osobu do systemu
        self.deal_id = 5711
        deal = DealFactory(id=self.deal_id, deal_typ="SU", hodnota=1996719745, dny_po_splatnosti=17,
                           zustatek_jistiny=1.550, datum_od="2019-02-06", datum_do="2023-06-13",
                           datum_zesplatneni="2023-08-11", owner='Květoslav Překližka', poslat_na_katastr=1,
                           poslat_vyzvu=1, stage="DPS 15-34", vyzva_moznost=None)

        self.bob_person_id = 222
        self.bob_fo_id = 33333
        self.bob_fop_id = 44444
        bob = PersonFOFactory(person_id=self.bob_person_id, id=self.bob_fo_id)
        podnikatel_bob = PersonFOPFactory(person_id=self.bob_person_id, id=self.bob_fop_id)
        PersonHasPersonFactory(person_fk=podnikatel_bob, fo_fk=bob, vztah="fop")
        DealHasPersonFactory(deal_fk=deal, person_fk=bob)
        DealHasPersonFactory(deal_fk=deal, person_fk=podnikatel_bob)

        self.ivan_po_id = 55555
        ivan = PersonPOFactory(id=self.ivan_po_id)
        DealHasPersonFactory(deal_fk=deal, person_fk=ivan)

    def test_fo_su(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.bob_fo_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.bob_fo_id)
        self.assertEqual(deal_has_peson_query.zadatel, 1)
        self.assertEqual(deal_has_peson_query.zastavce, 1)
        self.assertEqual(deal_has_peson_query.spoludluznik, 1)
        self.assertEqual(deal_has_peson_query.najemce, 0)
        self.assertEqual(deal_has_peson_query.prodavajici, 0)
        self.assertEqual(deal_has_peson_query.rucitel, 1)
        self.assertEqual(deal_has_peson_query.pristupitel, 1)

    def test_fop_su(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.bob_fop_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.bob_fop_id)
        self.assertEqual(deal_has_peson_query.zadatel, 0)
        self.assertEqual(deal_has_peson_query.zastavce, 0)
        self.assertEqual(deal_has_peson_query.spoludluznik, 0)
        self.assertEqual(deal_has_peson_query.najemce, 0)
        self.assertEqual(deal_has_peson_query.prodavajici, 0)
        self.assertEqual(deal_has_peson_query.rucitel, 1)
        self.assertEqual(deal_has_peson_query.pristupitel, 1)

    def test_po_su(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.ivan_po_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.ivan_po_id)
        self.assertEqual(deal_has_peson_query.zadatel, 0)
        self.assertEqual(deal_has_peson_query.zastavce, 1)
        self.assertEqual(deal_has_peson_query.spoludluznik, 0)
        self.assertEqual(deal_has_peson_query.najemce, 0)
        self.assertEqual(deal_has_peson_query.prodavajici, 0)
        self.assertEqual(deal_has_peson_query.rucitel, 0)
        self.assertEqual(deal_has_peson_query.pristupitel, 0)


class TestRoleOsobyDealVN(TestCase):
    def setUp(self):
        # Login and rules setup
        self.user = User.objects.create_user(username="testovaciuser", password="testovaciheslo")
        my_secret = "MYTESTSECRETCODE"
        UserSecretCode.objects.create(user_id=self.user.id, secret_key=my_secret)
        client.post("/login/", {"username": "testovaciuser", "password": "testovaciheslo"})
        self.user.user_permissions.add(Permission.objects.get(codename="view_deal"))

        # SetUp popisujici investicni uver, kde prvni vlkadame fizickou osobu do systemu
        self.deal_id = 5712
        deal = DealFactory(id=self.deal_id, deal_typ="VN", hodnota=1996719745, dny_po_splatnosti=17,
                           zustatek_jistiny=1.550, datum_od="2019-02-06", datum_do="2023-06-13",
                           datum_zesplatneni="2023-08-11", owner='Květoslav Překližka', poslat_na_katastr=1,
                           poslat_vyzvu=1, stage="DPS 15-34", vyzva_moznost=None)

        self.nasty_person_id = 123
        self.nasty_fo_id = 12345
        self.nasty_fop_id = 12346
        nasty = PersonFOFactory(person_id=self.nasty_person_id, id=self.nasty_fo_id)
        podnikatel_nasty = PersonFOPFactory(person_id=self.nasty_person_id, id=self.nasty_fop_id)
        PersonHasPersonFactory(person_fk=podnikatel_nasty, fo_fk=nasty, vztah="fop")
        DealHasPersonFactory(deal_fk=deal, person_fk=nasty)
        DealHasPersonFactory(deal_fk=deal, person_fk=podnikatel_nasty)

        self.petr_po_id = 77777
        petr = PersonPOFactory(id=self.petr_po_id)
        DealHasPersonFactory(deal_fk=deal, person_fk=petr)

    def test_fo_su(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.nasty_fo_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.nasty_fo_id)
        self.assertEqual(deal_has_peson_query.zadatel, 0)
        self.assertEqual(deal_has_peson_query.zastavce, 0)
        self.assertEqual(deal_has_peson_query.spoludluznik, 0)
        self.assertEqual(deal_has_peson_query.najemce, 1)
        self.assertEqual(deal_has_peson_query.prodavajici, 1)
        self.assertEqual(deal_has_peson_query.rucitel, 0)
        self.assertEqual(deal_has_peson_query.pristupitel, 0)

    def test_fop_su(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.nasty_fop_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.nasty_fop_id)
        self.assertEqual(deal_has_peson_query.zadatel, 0)
        self.assertEqual(deal_has_peson_query.zastavce, 0)
        self.assertEqual(deal_has_peson_query.spoludluznik, 0)
        self.assertEqual(deal_has_peson_query.najemce, 1)
        self.assertEqual(deal_has_peson_query.prodavajici, 1)
        self.assertEqual(deal_has_peson_query.rucitel, 0)
        self.assertEqual(deal_has_peson_query.pristupitel, 0)

    def test_po_su(self):
        client.post("/ajax/role/",
                    {"role": "zadatel,zastavce,spoludluznik,najemce,prodavajici,rucitel,pristupitel",
                     "deal_id": self.deal_id, "person_id": self.petr_po_id})
        deal_has_peson_query = DealHasPerson.objects.get(deal_fk=self.deal_id, person_fk=self.petr_po_id)
        self.assertEqual(deal_has_peson_query.zadatel, 0)
        self.assertEqual(deal_has_peson_query.zastavce, 0)
        self.assertEqual(deal_has_peson_query.spoludluznik, 0)
        self.assertEqual(deal_has_peson_query.najemce, 1)
        self.assertEqual(deal_has_peson_query.prodavajici, 1)
        self.assertEqual(deal_has_peson_query.rucitel, 0)
        self.assertEqual(deal_has_peson_query.pristupitel, 0)
