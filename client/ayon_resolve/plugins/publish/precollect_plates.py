import pyblish

from ayon_resolve.otio import utils


class PrecollectPlate(pyblish.api.InstancePlugin):
    """PreCollect new plates."""

    order = pyblish.api.CollectorOrder - 0.48
    label = "Precollect Plate"
    hosts = ["resolve"]
    families = ["plate"]

    def process(self, instance):
        """
        Args:
            instance (pyblish.Instance): The shot instance to update.
        """
        # Temporary disable no-representation failure.
        # TODO not sure what should happen for the plate.
        instance.data["folderPath"] = instance.data.pop("hierarchy_path")
        instance.data["families"].append("clip")

        # Adjust instance data from parent otio timeline.
        otio_timeline = instance.context.data["otioTimeline"]
        instance.data["fps"] = instance.context.data["fps"]

        otio_clip, _ = utils.get_marker_from_clip_index(
            otio_timeline, instance.data["clip_index"]
        )
        if not otio_clip:
            raise RuntimeError("Could not retrieve otioClip for shot %r", instance)

        instance.data["otioClip"] = otio_clip
