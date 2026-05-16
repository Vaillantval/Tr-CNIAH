# Re-export every model so that `from apps.core.models import X` keeps working.

from .content import (
    Newsletter,
    DocumentCategory,
    ReferenceDocument,
    VideoResource,
    ImageGallery,
)

from .membership import (
    MembershipDocument,
    CotisationDocument,
    DocumentHistorique,
)

from .formations import (
    CategoryFormation,
    FormationContent,
    FormationImage,
    HonneurMerite,
    HonneurMeriteImage,
)

from .members import (
    TitreProfessionnel,
    MembreActif,
    PageMembresActifs,
    ConfigurationCertificat,
    Certification,
)

from .complaints import (
    Plainte,
    DocumentPlainte,
)

from .governance import (
    ComiteDirection,
    MembreComite,
    CommissionApurement,
    MembreCommission,
    ConseilDiscipline,
    MembreConseil,
)

from .norms import (
    CategoryNorme,
    Norme,
)

from .sponsors import Sponsor

from .adhesion import DemandeAdhesion

__all__ = [
    "Newsletter",
    "DocumentCategory",
    "ReferenceDocument",
    "VideoResource",
    "ImageGallery",
    "MembershipDocument",
    "CotisationDocument",
    "DocumentHistorique",
    "CategoryFormation",
    "FormationContent",
    "FormationImage",
    "HonneurMerite",
    "HonneurMeriteImage",
    "TitreProfessionnel",
    "MembreActif",
    "PageMembresActifs",
    "ConfigurationCertificat",
    "Certification",
    "Plainte",
    "DocumentPlainte",
    "ComiteDirection",
    "MembreComite",
    "CommissionApurement",
    "MembreCommission",
    "ConseilDiscipline",
    "MembreConseil",
    "CategoryNorme",
    "Norme",
    "Sponsor",
    "DemandeAdhesion",
]
