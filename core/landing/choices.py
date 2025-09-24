from django.utils.translation import gettext_lazy as _

OPCIONES_COMPROBANTES = [
    ('D', _("Debe")),
    ('H', _("Haber")),
    ('I', _("Indistinto")),
]

OPCIONES_SALDO = [
    ('D', _('Deudora')),
    ('H', _('Acreedora')),
    ('I', _('Indistinto')),
    ('d', _('Indistinto normalmente deudora')),
    ('h', _('Indistinto normalmente acreedora')),
]