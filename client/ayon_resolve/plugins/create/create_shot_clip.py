import copy

from ayon_resolve.api import plugin, lib, constants
from ayon_resolve.api.lib import (
    get_video_track_names,
    create_bin,
)
from ayon_core.pipeline.create import CreatorError, CreatedInstance
from ayon_core.lib import BoolDef, EnumDef, TextDef, UILabelDef, NumberDef





class _ResolveInstanceCreator(plugin.HiddenResolvePublishCreator):
    """Wrapper class for shot product.
    """

    def create(self, instance_data, _):
        """Return a new CreateInstance for new shot from Resolve.

        Args:
            instance_data (dict): global data from original instance

        Return:
            CreatedInstance: The created instance object for the new shot.
        """
        hierarchy_path = (
            f'/{instance_data["hierarchy"]}/'
            f'{instance_data["hierarchyData"]["shot"]}'
        )
        instance_data.update({
            "productName": "shotMain",
            "label": f"{hierarchy_path} {self.product_type}",
            "productType": self.product_type,
            "hierarchy_path": hierarchy_path,
            "shotName": instance_data["hierarchyData"]["shot"]
        })

        new_instance = CreatedInstance(
            self.product_type, instance_data["productName"], instance_data, self
        )
        self._store_new_instance(new_instance)
        return new_instance        


class ResolveShotInstanceCreator(_ResolveInstanceCreator):
    """Shot product.
    """
    identifier = "io.ayon.creators.resolve.shot"
    product_type = "shot"    
    label = "Editorial Shot"


class EditorialReviewInstanceCreator(_ResolveInstanceCreator):
    """Review product type class

    Review representation instance.
    """
    identifier = "io.ayon.creators.resolve.review"
    product_type = "review"
    label = "Editorial Review"


class CreateShotClip(plugin.ResolveCreator):
    """Publishable clip"""

    identifier = "io.ayon.creators.resolve.clip"
    label = "Create Publishable Clip"
    product_type = "editorial"
    icon = "film"
    defaults = ["Main"]

#    create_allow_context_change = False  
# TODO: explain consequence on folderPath
# https://github.com/ynput/ayon-core/blob/6a07de6eb904c139f6d346fd6f2a7d5042274c71/client/ayon_core/tools/publisher/widgets/create_widget.py#L732

    create_allow_thumbnail = False

    def get_pre_create_attr_defs(self):

        def header_label(text):
            return f"<br><b>{text}</b>"

        tokens_help = """\nUsable tokens:
    {_clip_}: name of used clip
    {_track_}: name of parent track layer
    {_sequence_}: name of parent sequence (timeline)"""
        gui_tracks = get_video_track_names()

        # Project settings might be applied to this creator via
        # the inherited `Creator.apply_settings`
        presets = self.presets

        return [

            BoolDef("use_selection",
                    label="Use only clips with <b>Chocolate</b>  clip color",
                    tooltip=(
                        "When enabled only clips of Chocolate clip color are "
                        "considered.\n\n"
                        "Acts as a replacement to 'Use selection' because "
                        "Resolves API exposes no functionality to retrieve "
                        "the currently selected timeline items."
                    ),
                    default=True),

            # renameHierarchy
            UILabelDef(
                label=header_label("Shot Hierarchy And Rename Settings")
            ),
            TextDef(
                "hierarchy",
                label="Shot Parent Hierarchy",
                tooltip="Parents folder for shot root folder, "
                        "Template filled with *Hierarchy Data* section",
                default=presets.get("hierarchy", "{folder}/{sequence}"),
            ),
            BoolDef(
                "clipRename",
                label="Rename clips",
                tooltip="Renaming selected clips on fly",
                default=presets.get("clipRename", False),
            ),
            TextDef(
                "clipName",
                label="Clip Name Template",
                tooltip="template for creating shot names, used for "
                        "renaming (use rename: on)",
                default=presets.get("clipName", "{sequence}{shot}"),
            ),
            NumberDef(
                "countFrom",
                label="Count sequence from",
                tooltip="Set where the sequence number starts from",
                default=presets.get("countFrom", 10),
            ),
            NumberDef(
                "countSteps",
                label="Stepping number",
                tooltip="What number is adding every new step",
                default=presets.get("countSteps", 10),
            ),

            # hierarchyData
            UILabelDef(
                label=header_label("Shot Template Keywords")
            ),
            TextDef(
                "folder",
                label="{folder}",
                tooltip="Name of folder used for root of generated shots.\n"
                        f"{tokens_help}",
                default=presets.get("folder", "shots"),
            ),
            TextDef(
                "episode",
                label="{episode}",
                tooltip=f"Name of episode.\n{tokens_help}",
                default=presets.get("episode", "ep01"),
            ),
            TextDef(
                "sequence",
                label="{sequence}",
                tooltip=f"Name of sequence of shots.\n{tokens_help}",
                default=presets.get("sequence", "sq01"),
            ),
            TextDef(
                "track",
                label="{track}",
                tooltip=f"Name of timeline track.\n{tokens_help}",
                default=presets.get("track", "{_track_}"),
            ),
            TextDef(
                "shot",
                label="{shot}",
                tooltip="Name of shot. '#' is converted to padded number."
                        f"\n{tokens_help}",
                default=presets.get("shot", "sh###"),
            ),

            # verticalSync
            UILabelDef(
                label=header_label("Vertical Synchronization Of Attributes")
            ),
            BoolDef(
                "vSyncOn",
                label="Enable Vertical Sync",
                tooltip="Switch on if you want clips above "
                        "each other to share its attributes",
                default=presets.get("vSyncOn", True),
            ),
            EnumDef(
                "vSyncTrack",
                label="Hero track",
                tooltip="Select driving track name which should "
                        "be mastering all others",
                items=gui_tracks or ["<nothing to select>"],
            ),

            # publishSettings
            UILabelDef(
                label=header_label("Publish Settings")
            ),
            EnumDef(
                "variant",
                label="Product Variant",
                tooltip="Chose variant which will be then used for "
                        "product name, if <track_name> "
                        "is selected, name of track layer will be used",
                items=['<track_name>', 'main', 'bg', 'fg', 'bg', 'animatic'],
            ),
            EnumDef(
                "productType",
                label="Product Type",
                tooltip="How the product will be used",
                items=['plate'],  # it is prepared for more types
            ),
            EnumDef(
                "reviewTrack",
                label="Use Review Track",
                tooltip="Generate preview videos on fly, if "
                        "'< none >' is defined nothing will be generated.",
                items=['< none >'] + gui_tracks,
            ),
            BoolDef(
                "audio",
                label="Include audio",
                tooltip="Process subsets with corresponding audio",
                default=False,
            ),
            BoolDef(
                "sourceResolution",
                label="Source resolution",
                tooltip="Is resoloution taken from timeline or source?",
                default=False,
            ),

            # shotAttr
            UILabelDef(
                label=header_label("Shot Attributes"),
            ),
            NumberDef(
                "workfileFrameStart",
                label="Workfiles Start Frame",
                tooltip="Set workfile starting frame number",
                default=presets.get("workfileFrameStart", 1001),
            ),
            NumberDef(
                "handleStart",
                label="Handle start (head)",
                tooltip="Handle at start of clip",
                default=presets.get("handleStart", 0),
            ),
            NumberDef(
                "handleEnd",
                label="Handle end (tail)",
                tooltip="Handle at end of clip",
                default=presets.get("handleEnd", 0),
            ),
        ]

    presets = None
    rename_index = 0

    def create(self, subset_name, instance_data, pre_create_data):
        super(CreateShotClip, self).create(subset_name,
                                           instance_data,
                                           pre_create_data)

        if not self.timeline:
            raise CreatorError(
                "You must be in an active timeline to "
                "create the publishable clips.\n\n"
                "Go into a timeline and then reset the publisher."
            )

        if not self.selected:
            if pre_create_data.get("use_selection", False):
                raise CreatorError(
                    "No Chocolate-colored clips found from "
                    "timeline.\n\n Try changing clip(s) color "
                    "or disable clip color restriction."
                )
            else:
                raise CreatorError(
                    "No clips found on current timeline."
                )

        self.log.info(f"Selected: {self.selected}")

        # Todo detect audio but no audio track.
        # warning

        # sort selected trackItems by vSync track
        sorted_selected_track_items = []
        unsorted_selected_track_items = []
        v_sync_track = pre_create_data.get("vSyncTrack", "")
        for track_item_data in self.selected:
            if track_item_data["track"]["name"] in v_sync_track:
                sorted_selected_track_items.append(track_item_data)
            else:
                unsorted_selected_track_items.append(track_item_data)

        sorted_selected_track_items.extend(unsorted_selected_track_items)

        # create media bin for compound clips (trackItems)
        media_pool_folder = create_bin(self.timeline.GetName())

        instances = []
        for index, track_item_data in enumerate(sorted_selected_track_items):
            self.log.info(
                "Processing track item data: {}".format(track_item_data)
            )

            instance_data.update({
                "clip_index": index,
                "newHierarchyIntegration": True,
                # Backwards compatible (Deprecated since 24/06/06)
                "newAssetPublishing": True,
            })

            # convert track item to timeline media pool item
            publish_clip = plugin.PublishableClip(
                track_item_data,
                pre_create_data,
                media_pool_folder,
                rename_index=index,
                data=instance_data
            )

            track_item = publish_clip.convert()
            if track_item is None:
                # Ignore input clips that do not convert into a track item
                # from `PublishableClip.convert`
                continue

            track_item.SetClipColor(constants.publish_clip_color)

            instance_data = copy.deepcopy(instance_data)
            # TODO: here we need to replicate Traypublisher Editorial workflow
            #  and create shot, plate, review, and audio instances with own
            #  dedicated plugin
            for creator_id in (
                "io.ayon.creators.resolve.shot",
                "io.ayon.creators.resolve.review",
            ): 
                instance = self.create_context.creators[creator_id].create(
                    instance_data, None
                )
                instance.transient_data["track_item"] = track_item            
                self._add_instance_to_context(instance)
                instances.append(instance)

            # self.imprint_instance_node(instance_node,
            #                            data=instance.data_to_store())
        return instances

    def collect_instances(self):
        """Collect all created instances from current timeline."""
        selected_timeline_items = lib.get_current_timeline_items(
            filter=True, selecting_color=constants.publish_clip_color)

        instances = []
        for timeline_item_data in selected_timeline_items:
            timeline_item = timeline_item_data["clip"]["item"]

            # get openpype tag data
            tag_data = lib.get_timeline_item_ayon_tag(timeline_item)
            if not tag_data:
                continue

            instance = CreatedInstance.from_existing(tag_data, self)
            instance.transient_data["track_item"] = timeline_item
            self._add_instance_to_context(instance)

        return instances

    def update_instances(self, update_list):
        """Store changes of existing instances so they can be recollected.

        Args:
            update_list(List[UpdateData]): Gets list of tuples. Each item
                contain changed instance and it's changes.
        """
        for created_inst, _changes in update_list:
            track_item = created_inst.transient_data["track_item"]
            data = created_inst.data_to_store()
            self.log.info(f"Storing data: {data}")

            lib.imprint(track_item, data)

    def remove_instances(self, instances):
        """Remove instance marker from track item.

        Args:
            instance(List[CreatedInstance]): Instance objects which should be
                removed.
        """
        for instance in instances:
            track_item = instance.transient_data["track_item"]

            # removing instance by marker color
            print(f"Removing instance: {track_item.GetName()}")
            track_item.DeleteMarkersByColor(constants.ayon_marker_color)

            self._remove_instance_from_context(instance)
