"""

Trajectory Tracker: track mouse/finger movement

@author: Dror Dotan
@copyright: Copyright (c) 2017, Dror Dotan
"""

import numbers

import expyriment

import dobbyt
import dobbyt._utils as _u


# noinspection PyAttributeOutsideInit
class TrajectoryTracker(dobbyt._DobbyObject):

    _errmsg_set_to_non_boolean = "dobbyt error: invalid attempt to set TrajectoryTracker.{0} to a non-boolean value ({1})"
    _errmsg_non_numeric_coord = "dobbyt error in TrajectoryTracker.mouse_at(): the {0} is a non-numeric value ({1})"
    _errmsg_negative_time = "dobbyt error in TrajectoryTracker.mouse_at(): negative time ({1}) is invalid"


    #----------------------------------------------------
    def __init__(self):
        """
        Constructor
        :param tracking_active: See :func:`~dobbyt.movement.TrajectoryTracker.tracking_active` (default=False).
        """
        super(TrajectoryTracker, self).__init__()
        self.reset(False)
        self._filename = None

    #----------------------------------------------------
    @property
    def tracking_active(self):
        """ Whether tracking is currently active (boolean). When inactive, calls to update_xyt() will be ignored. """
        return self._tracking_active

    @tracking_active.setter
    def tracking_active(self, value):
        _u.validate_attr_type(self, "tracking_active", value, bool)
        self._tracking_active = value
        self._log_setter("tracking_active")


    #----------------------------------------------------
    def reset(self, tracking_active=None):
        """
        Forget any previously-tracked points.
        :param tracking_active: Whether to activate or deactivate tracking. Default: None (don't change)
        """
        if tracking_active is not None:
            self.tracking_active = tracking_active

        self._trajectory = {'x' : [], 'y' : [], 'time' : []}

        if self._log_level:
            expyriment._active_exp._event_file_log("Trajectory,Reset", 1)

    #----------------------------------------------------
    def update_xyt(self, x_coord, y_coord, time):
        """
        Track a point.
        If tracking is currently inactive, this function will do nothing.
        """

        if not self._tracking_active:
            return

        _u.validate_func_arg_type(self, "update_xyt", "x_coord", x_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "y_coord", y_coord, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "time", time, numbers.Number)
        _u.validate_func_arg_type(self, "update_xyt", "time", time, numbers.Number)

        if time < 0:
            raise ValueError(TrajectoryTracker._errmsg_negative_time.format(time))

        self._trajectory['x'].append(x_coord)
        self._trajectory['y'].append(y_coord)
        self._trajectory['time'].append(time)

        if self._log_level:
            expyriment._active_exp._event_file_log("Trajectory,Track_xyt,{0},{1},{2}".format(x_coord, y_coord, time), 2)

    #----------------------------------------------------
    def get_xyt(self):
        """
        Get a list of (x,y,time) tuples - one per tracked point
        """
        trj = self._trajectory
        return zip(trj['x'], trj['y'], trj['time'])

    #----------------------------------------------------
    def init_output_file(self, filename, xy_precision=5, time_precision=3):
        """
        Initialize a new CSV output file for saving the results
        :param filename: Full path
        :param xy_precision: Precision of x,y coordinates (default: 5)
        :param time_precision: Precision of time (default: 3)
        """
        self._filename = filename
        self._xy_precision = xy_precision
        self._time_precision = time_precision

        fh = self._open_file(filename, 'w')
        fh.write('trial,time,x,y\n')
        fh.close()

        if self._log_level:
            expyriment._active_exp._event_file_log(
                "Trajectory,InitOutputFile,%s" % self._filename, 2)

    #----------------------------------------------------
    def save_to_file(self, trial_num):
        """
        Save the tracked trajectory (ever since the last reset() call) to a CSV file
        :param trial_num:
        :return: The number of rows printed to the file
        """
        if self._filename is None:
            raise dobbyt.InvalidStateError('TrajectoryTracker.save_to_file() was called before calling init_output_file()')

        fh = self._open_file(self._filename, 'a')

        rows = self.get_xyt()
        for x, y, t in rows:
            x = ('%d' % x) if isinstance(x, int) else '%.*f' % (self._xy_precision, x)
            y = ('%d' % y) if isinstance(y, int) else '%.*f' % (self._xy_precision, y)
            fh.write("%d,%.*f,%s,%s\n" % (trial_num, self._time_precision, t, x, y))

        fh.close()

        if self._log_level:
            expyriment._active_exp._event_file_log(
                "Trajectory,SavedTrial,%s,%d,%d" % (self._filename, trial_num, len(rows)), 2)

        return len(rows)

    #----------------------------------------------------
    # Default implementation for opening an output file
    #
    def _open_file(self, filename, mode):
        return open(filename, mode)
