import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View

from config import models
from jana.utils.decorators import logged_in
from jana.utils.jana_log import make_log_entry

# This Class-Based View contains the logic for changing the roles
# of the person's entity (our credit client) in the system
class RoleView(View):
    # This dictionary indicates the possible roles that we can set to the requested person,
    # depending on the type of person and the type of deal
    role_rules_dictionary = {
        # Where the first level key is the Deal type
        "SU": {
            # Where the second level key is of type Person
            "FO": ["zadatel", "spoludluznik", "zastavce", "rucitel", "pristupitel"],
            "FOP": ["rucitel", "pristupitel"],
            "PO": ["zastavce"]
        },
        "IU": {
            "FO": ["zastavce", "rucitel", "pristupitel"],
            "FOP": ["zadatel", "spoludluznik", "rucitel", "pristupitel"],
            "PO": ["zadatel", "spoludluznik", "zastavce", "rucitel", "pristupitel"]
        },
        "VN": {
            "FO": ["najemce", "prodavajici"],
            "FOP": ["najemce", "prodavajici"],
            "PO": ["najemce", "prodavajici"]
        },
    }

    # The method processes a Post request to change the role of a person
    def post(self, request):
        try:
            role = request.POST.get("role").split(",")
            deal = models.Deal.objects.get(id=request.POST.get("deal_id"))
            person_from_request = models.Person.objects.get(id=request.POST.get("person_id"))
            deal_has_person = None

            try:
                deal_has_person = models.DealHasPerson.objects.get(deal_fk=deal, person_fk=person_from_request)
            except ObjectDoesNotExist:
                pass

            if deal_has_person:
                deal_has_person.set_default_role()
            else:
                deal_has_person = models.DealHasPerson.objects.create(
                    deal_fk=deal,
                    person_fk=person_from_request,
                    zadatel=0,
                    zastavce=0,
                    spoludluznik=0,
                    najemce=0,
                    prodavajici=0,
                    rucitel=0,
                    pristupitel=0
                )

            for role_item in role:
                self.set_role(deal_has_person, role_item,
                              self.role_rules_dictionary[deal.deal_typ][person_from_request.prav_subjekt])
            deal_has_person.save()
            deal_has_person.refresh_from_db()

            make_log_entry(
                request, method=request.method, data={"deal_has_person": deal_has_person, "request": request.POST}
            )

            if models.DealHasPerson.objects.filter(deal_fk=deal, zadatel=1).count() > 1:
                deal_has_person.zadatel = 0
                deal_has_person.save()
                return HttpResponse("Vice nez jeden zadatel")
            return HttpResponse("Vsechno v poradku")
        except Exception:
            make_log_entry(
                request, method=request.method, data={"error": Exception, "request": request.POST}
            )
            return HttpResponse(403)

    def set_role(self, deal_has_person, role_item, role_rules_dictionary):
        if role_item in role_rules_dictionary:
            setattr(deal_has_person, role_item, 1)


@logged_in
def nz_aktivace_pokuty_view(request):
    """
    Handles request for aktivace pokuty. Saves recieved date to Nz.datm_aktivace and redirects to nz_detail_view
    """
    nz = get_object_or_404(models.Nz, pk=request.POST.get("nz"))
    datum = datetime.strptime(request.POST.get("date"), "%Y-%m-%d")
    nz.datum_aktivace = datum.date()
    nz.save()
    make_log_entry(request, method=request.method, data={"nz": nz, "request": request.POST})

    return redirect("nz_detail_view", nz_id=nz.id)
