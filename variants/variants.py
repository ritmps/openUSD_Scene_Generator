from pxr import Usd, UsdGeom, Sdf 

def create_variant_set(prim, variant_set_name, variant_names):
    """
    Create a variant set on the given prim.

    Args:
        prim (Usd.Prim): The prim to create the variant set on.
        variant_set_name (str): The name of the variant set.
        variant_names (list): List of variant names to add.
    Returns:
        Usd.VariantSet: The created variant set
    """
    variant_set = prim.GetVariantSets().AddVariantSet(variant_set_name)
    for name in variant_names:
        variant_set.AddVariant(name)
    return variant_set

def populate_variant(prim, variant_set_name, variant_name, authoring_fn):
    """
    Author content inside a variant.

    Args:
        prim(Usd.Prim): The prim to author variants on.
        variant_set_name (str): The name of the variant set.
        variant_name (str): The specific variant to author.
        authoring_fn (function): A function that takes a Usd.Stage and performs authoring.
    """
    variant_set = prim.GetVariantSets().GetVariantSet(variant_set_name)
    variant_set.SetVariantSelection(variant_name)

    with variant_set.GetVariantEditContext():
        authoring_fn(prim.GetStage())

def switch_variant(prim, variant_set_name, variant_name):
    """
    Switch to a specific variant.

    Args:
        prim (Usd.Prim): The prim to switch variants on.
        variant_set_name (str): The name of the variant set.
        variant_name (str): The variant to select.
    """
    variant_set = prim.GetVariantSets().GetVariantSet(variant_set_name)
    variant_set.SetVariantSelection(variant_name)