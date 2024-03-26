import squeeze
from flask import Flask, render_template, request
from plotly import utils
from json import dumps

app = Flask(__name__, template_folder='template')


@app.route('/ticker', methods=["POST"])
def graph_ticker():
    ticker = request.form.get("ticker")
    period = request.form.get("period")
    app.logger.info(f'{ticker} {period}')
    df, enter_long, enter_short = squeeze.get_ttm_squeeze(ticker, period)
    app.logger.info(f'enter long: {enter_long} || enter_short: {enter_short}')
    graph = squeeze.chart(df)
    all_pub_json = dumps(graph, cls=utils.PlotlyJSONEncoder)
    return render_template('graph.html', graphJSON=all_pub_json)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
   app.run(debug=True)
