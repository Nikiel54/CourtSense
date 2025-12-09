import Card from "../Card"

export function PredictionDashboard() {

    return (
        <main className="page-body">
            <div className="instructions">
                <h1>Select Teams to Predict the Outcome</h1>
                <em>Choose a home team and and away team to see the prediction</em>
                <Card>
                    <form action="post">
                        <label htmlFor="">
                            Home Team
                            <select name="Home Team">
                                <option value="Team A" data>Team A</option>
                            </select>
                        </label>
                    </form>
                </Card>
            </div>
        </main>
    )
}