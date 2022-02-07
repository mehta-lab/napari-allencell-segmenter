# Hook specifications: https://napari.org/docs/dev/plugins/hook_specifications.html
import napari

from napari_allencell_segmenter.core.application import Application
# from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
import dask.array as da
from waveorder.io import WaveorderReader
import zarr


"""
The class name here gets converted to title case and gets displayed as both the title 
of the plugin window and the title displayed in the app menu dropdown.
"""


class WorkflowEditorWidget(QWidget):  # pragma: no-cover
    def __init__(self, napari_viewer: napari.Viewer):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self._application = Application(napari_viewer, self.layout())
        self._application.router.workflow_selection()  # Initialize first screen


class BatchProcessingWidget(QWidget):
    def __init__(self, napari_viewer: napari.Viewer):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.MinimumExpanding)
        self.setLayout(QVBoxLayout())
        self._application = Application(napari_viewer, self.layout())
        self._application.router.batch_processing()  # Initialize first screen


def ome_zarr_reader(path):
    reader = WaveorderReader(path)
    results = list()

    zs = zarr.open(path, 'r')
    names = []

    dict_ = zs.attrs.asdict()
    wells = dict_['plate']['wells']
    for well in wells:
        path = well['path']
        well_dict = zs[path].attrs.asdict()
        for name in well_dict['well']['images']:
            names.append(name['path'])
    for pos in range(reader.get_num_positions()):
        meta = dict()
        name = names[pos]
        meta['name'] = name
        results.append((da.from_zarr(reader.get_zarr(pos)), meta))

    return results


def napari_get_reader(path: str):
    print('here')
    """Returns a reader for supported paths that include IDR ID.
    - URL of the form: https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.1/ID.zarr/
    """

    if isinstance(path, str) and path.endswith(".zarr"):
        # If we recognize the format, we return the actual reader function
        return ome_zarr_reader

    # Ignoring this path
    else:
        return None


def napari_experimental_provide_dock_widget():  # pragma: no-cover
    return [(WorkflowEditorWidget, {"name": "Workflow editor"}), (BatchProcessingWidget, {"name": "Batch processing"})]
