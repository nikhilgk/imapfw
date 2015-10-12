
from ..managers.manager import Manager
from ..drivers.driver import DriverInterface
from ..types.repository import RepositoryInterface
from ..constants import DRV


class DriverManagerInterface(object):
    pass # TODO


class DriverManager(Manager, DriverManagerInterface):
    """The driver manager.

    The receiver builds and runs the low-level driver (from rascal api.drivers).

    All the api.drivers types use the same DriverInterface interface. This
    interface is low-level interface which is not directly mapped as the public
    DriverManager interface.

    The user of the emitter controls both the worker and the driver. The user of
    the emitter change over time."""

    def __init__(self, ui, concurrency, workerName, rascal):
        super(DriverManager, self).__init__(ui, concurrency, workerName)

        self._rascal = rascal

        self._driver = None
        self._folders = None

        ui.debugC(DRV, "%s manager created"% workerName)

    def exposed_connect_nowait(self):
        connected = self._driver.connect()
        self.ui.debugC(DRV, "driver connected")
        if not connected:
            raise Exception("%s: could not connect the driver"% self.workerName)

    def exposed_fetchFolders_nowait(self):
        self.ui.debugC(DRV, "starting fetch of folders")
        self._folders = self._driver.getFolders()

    def exposed_getFolders(self):
        self.ui.debugC(DRV, "folders: %s"% self._folders)
        return self._folders

    def exposed_startDriver(self, typeName):
        # Retrieve the driver class from the type.
        typeInst = self._rascal.get(typeName, [RepositoryInterface]) #TODO: defaultConstructor
        self._driver = typeInst.driver()

        # Sanity check.
        if not isinstance(self._driver, DriverInterface):
            raise Exception("driver class %s does not satisfy DriverInterface"%
                self._driver.__class__.__name__)

        self.ui.debugC(DRV, "starting driver '%s' of '%s'"%
            (self._driver.getClassName(), typeName))


def createSideDriverManager(ui, concurrency, rascal, HandlerName, number):
    """Enable the driver machinery for one side.

    Helper when two drivers are required, one for each side, each running
    concurrently."""

    driverName = "%s.Driver.%s"% (HandlerName, number)

    # Build the driver.
    drivermanager = DriverManager(
        ui,
        concurrency,
        driverName,
        rascal,
        )
    emitter, receiver = drivermanager.split()
    return emitter, receiver