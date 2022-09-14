import plotly.graph_objects as go
import plotly.offline as pyo

class RHOptionPlotter():

    def __init__(self):
        self.fig = None

    def plot(self, plot_data):
        # TODO confirm that pandas column-wise min and max are giving the correct normalization result for the figure
        min_val = plot_data.min()
        max_val = plot_data.max()

        normalized_plot_data=(plot_data-min_val)/(max_val-min_val)
        normalized_plot_data.fillna(0, inplace=True)

        figure_data = []
        for system_description, tech_data in normalized_plot_data.iterrows():
            figure_data.append(go.Scatter(
                x = plot_data.columns.values,
                y = tech_data,
                name = system_description,
                # hovertemplate="D: %{plot_data.loc[system_description]}"
                # hoverinfo=f"{plot_data.loc[system_description]}"
                hoverlabel={"namelength":-1},
                hovertext=plot_data.loc[system_description]
            ))

        self.fig = go.Figure(
            data = figure_data,
            layout=go.Layout(
                title=go.layout.Title(text='Power configuration comparison'),
                showlegend=True
            )
        )
        self.fig.update_layout(legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.1,
            xanchor="left",
            x=0
        ))

        pyo.plot(self.fig)

    def save(self, filepath):
        self.fig.write_html(filepath)