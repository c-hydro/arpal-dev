# -------------------------------------------------------------------------------------
# Libraries
import logging
import numpy as np
import pandas as pd

import matplotlib.pylab as plt
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to plot scenarios against event
def plot_scenarios_rain2sm(file_data, file_path,
                           var_x='soil_moisture', var_y='rain', var_z='event_index', var_time='time',
                           var_x_limits=None, var_y_limits=None, var_z_limits=None,
                           event_n_min=0, event_n_max=None, event_label=True, season_label='NA',
                           figure_dpi=120, extra_args=None,
                           axes_x_template='soil moisture {:} [-]',
                           axes_y_template='rain accumulated {:} [mm]'):

    # Default argument(s)
    if var_x_limits is None:
        var_x_limits = [0, 1]
    if var_z_limits is None:
        var_z_limits = [0, 4]

    # Get datasets
    var_time = list(file_data[var_time].values)
    var_data_x = file_data[var_x].values
    var_data_z = file_data[var_z].values

    if var_time.__len__() > 0:

        var_time_from_ref = pd.Timestamp(var_time[-1]).strftime('%Y-%m-%d')
        var_time_to_ref = pd.Timestamp(var_time[0]).strftime('%Y-%m-%d')

        var_p95_x = np.percentile(var_data_x, 95)
        var_p99_x = np.percentile(var_data_x, 99)

        var_p95_str = '{0:.2f}'.format(var_p95_x)
        var_p99_str = '{0:.2f}'.format(var_p99_x)

        if 'rain_type' in list(extra_args.keys()):
            rain_type = extra_args['rain_type']
        else:
            logging.error(' ===> Rain Type is not defined in settings')
            raise IOError('Variable is not correctly defined')

        if 'soil_moisture_type' in list(extra_args.keys()):
            sm_type = extra_args['soil_moisture_type']
        else:
            logging.error(' ===> SoilMoisture Type is not defined in settings')
            raise IOError('Variable is not correctly defined')

        for rain_type_step in rain_type:

            if ('var_rain' in file_path) and ('var_sm' not in file_path):
                file_path_step = file_path.replace('var_rain', ':').format(rain_type_step)
            elif ('var_rain' in file_path) and ('var_sm' in file_path):
                file_path_step = file_path.replace('var_rain', ':')
                file_path_step = file_path_step.replace('var_sm', ':')
                file_path_step = file_path_step.format(rain_type_step, sm_type)
            else:
                logging.error(' ===> File path filling failed')
                raise NotImplementedError('Case not implemented yet')

            var_y_step = var_y.format(rain_type_step)
            var_data_y = file_data[var_y_step].values

            axis_y_step = axes_y_template.format(rain_type_step)
            axis_x_step = axes_x_template.format(sm_type)

            # Open figure
            fig = plt.figure(figsize=(17, 11))
            fig.autofmt_xdate()

            axes = plt.axes()
            axes.autoscale(True)

            p95 = axes.axvline(var_p95_x, color='#FFA500', linestyle='-', lw=2, label='95%')
            plt.text(var_p95_x, -0.02, var_p95_str, transform=axes.get_xaxis_transform(), ha='center', va='center')
            p99 = axes.axvline(var_p99_x, color='#FF0000', linestyle='-', lw=2, label='99%')
            plt.text(var_p99_x, -0.02, var_p99_str, transform=axes.get_xaxis_transform(), ha='center', va='center')

            colors = {0: 'grey', 1: 'green', 2: 'yellow', 3: 'orange', 4: 'red'}
            for t, x, y, z in zip(var_time, var_data_x, var_data_y, var_data_z):

                t = pd.Timestamp(t)

                if y >= 0:
                    color = colors[z]
                    p1 = axes.scatter(x, y, alpha=1, color=color, s=20)

                    if event_label:
                        if z > event_n_min:
                            label = t.strftime('%Y-%m-%d')
                            plt.annotate(label,  # this is the text
                                         (x, y),  # this is the point to label
                                         textcoords="offset points",  # how to position the text
                                         xytext=(0, 5),  # distance from text to points (x,y)
                                         ha='center')  # horizontal alignment can be left, right or center
                else:
                    logging.warning(' ===> Value of y is negative (' + str(y) + ') at time ' + str(t))

            axes.set_xlabel(axis_x_step, color='#000000', fontsize=14, fontdict=dict(weight='medium'))
            axes.set_xlim(var_x_limits[0], var_x_limits[1] )
            axes.set_ylabel(axis_y_step, color='#000000', fontsize=14, fontdict=dict(weight='medium'))
            if var_y_limits is not None:
                axes.set_ylim(var_y_limits[0], var_y_limits[1])

            xticks_list = axes.get_xticks().tolist()
            xticks_list.insert(0, -0.01)
            xticks_list.insert(len(xticks_list), 1.01)
            axes.set_xticks(xticks_list)
            axes.set_xticklabels(['', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0', ''], fontsize=12)

            legend = axes.legend((p95, p99), ('95%', '99%'), frameon=True, ncol=3, loc=9)
            axes.add_artist(legend)

            axes.grid(b=False, color='grey', linestyle='-', linewidth=0.5, alpha=1)

            axes.set_title(' #### Scenarios - Rain and Soil Moisture #### \n ' +
                           'TimePeriod :: ' + var_time_from_ref + ' - ' + var_time_to_ref + ' Season:: ' + season_label,
                           fontdict=dict(fontsize=16, fontweight='bold'))

            # plt.show()

            fig.savefig(file_path_step, dpi=figure_dpi)
            plt.close()

    else:
        logging.warning(' ===> Events are None for season ' + season_label)

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to plot scenarios against event
def plot_scenarios_sm2event(file_data, file_path, var_ref='soil_moisture', var_dep='event_index',
                         var_ref_limits=None, var_dep_limits=None, event_n_min=0, event_label=True,
                         figure_dpi=120):

    # Default argument(s)
    if var_ref_limits is None:
        var_ref_limits = [0, 1]
    if var_dep_limits is None:
        var_dep_limits = [0, 4]

    # Get datasets
    var_time_ref = list(file_data[var_ref].index)
    var_data_ref = file_data[var_ref].values
    var_data_dep = file_data[var_dep].values

    var_p95_ref = np.percentile(var_data_ref, 95)
    var_p99_ref = np.percentile(var_data_ref, 99)

    var_time_from_ref = var_time_ref[-1].strftime('%Y-%m-%d')
    var_time_to_ref = var_time_ref[0].strftime('%Y-%m-%d')

    var_p95_str = '{0:.2f}'.format(var_p95_ref)
    var_p99_str = '{0:.2f}'.format(var_p99_ref)

    # Open figure
    fig = plt.figure(figsize=(17, 11))
    fig.autofmt_xdate()

    axes = plt.axes()
    axes.autoscale(True)

    p1 = axes.plot(var_data_ref, var_data_dep, color='#33A1C9', linestyle='--', lw=0, marker='o', ms=10)
    p2 = axes.axvline(var_p95_ref, color='#FFA500', linestyle='-', lw=2, label='95%')
    plt.text(var_p95_ref, -0.02, var_p95_str, transform=axes.get_xaxis_transform(), ha='center', va='center')
    p3 = axes.axvline(var_p99_ref, color='#FF0000', linestyle='-', lw=2, label='99%')
    plt.text(var_p99_ref, -0.02, var_p99_str, transform=axes.get_xaxis_transform(), ha='center', va='center')

    axes.set_xlabel('soil moisture [-]', color='#000000', fontsize=14, fontdict=dict(weight='medium'))
    axes.set_xlim(var_ref_limits[0], var_ref_limits[1] )
    axes.set_ylabel('scenarios [-]', color='#000000', fontsize=14, fontdict=dict(weight='medium'))
    axes.set_ylim(var_dep_limits[0], var_dep_limits[1])

    xticks_list = axes.get_xticks().tolist()
    xticks_list.insert(0, -0.01)
    xticks_list.insert(len(xticks_list), 1.01)
    axes.set_xticks(xticks_list)
    axes.set_xticklabels(['', '0.0', '0.2', '0.4', '0.6', '0.8', '1.0', ''], fontsize=12)
    axes.set_yticks([-0.08, 0, 1, 2, 3, 4, 4.08])
    axes.set_yticklabels(['', 'white', 'green', 'yellow', 'orange', 'red', ''], fontsize=12)
    colors = ['', 'gray', 'green', 'yellow', 'orange', 'red', '']
    for color, tick in zip(colors, axes.yaxis.get_major_ticks()):
        tick.label1.set_color(color)

    legend = axes.legend((p1[0], p2, p3), ('event n', '95%', '99%'), frameon=True, ncol=3, loc=9)
    axes.add_artist(legend)

    axes.grid(b=False, color='grey', linestyle='-', linewidth=0.5, alpha=1)

    axes.set_title(' #### Scenarios - Events and Soil Moisture #### \n ' +
                   'TimePeriod :: ' + var_time_from_ref + ' - ' + var_time_to_ref,
                   fontdict=dict(fontsize=16, fontweight='bold'))

    if event_label:
        for t, x, y in zip(var_time_ref, var_data_ref, var_data_dep):
            if y > event_n_min:
                label = t.strftime('%Y-%m-%d')
                plt.annotate(label,  # this is the text
                             (x, y),  # this is the point to label
                             textcoords="offset points",  # how to position the text
                             xytext=(0, 5),  # distance from text to points (x,y)
                             ha='center')  # horizontal alignment can be left, right or center

    #plt.show()

    fig.savefig(file_path, dpi=figure_dpi)
    plt.close()

# -------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------
# Method to plot scenarios against accumulated maximum rain
def plot_scenarios_rain2event(file_data, file_path, var_ref='rain', var_list=['3H', '6H', '9H', '12H', '24H']):
    pass
# -------------------------------------------------------------------------------------
