import Card from "../Card";
import { useState } from "react";
import { TeamSelectionForm } from "./TeamSelectionForm"
import { PredictionResults } from "./PredictionResults";
import { usePredictions } from "../../customhooks/predictionFetching";

export function PredictionDashboard({ teamData }) {
    const [homeTeam, setHomeTeam] = useState(""); // data for filled out fields
    const [awayTeam, setAwayTeam] = useState("");
    const [homeTeamError, setHomeTeamError] = useState(false); // data for incorrectly filled out field states
    const [awayTeamError, setAwayTeamError] = useState(false);
    const [sameTeamSelectionError, setSameTeamSelectionError] = useState(false); // checks to ensure we don't call predictions on same team
    const [isSubmitted, setIsSubmitted] = useState(false); // controls if to call api for predictions

    const { prediction, error, loading } = usePredictions(homeTeam.id, awayTeam.id, isSubmitted, () => setIsSubmitted(false)); // track status of data

    
    function checkForTeamSelections() {
        if (homeTeam.name === awayTeam.name) { // if same team selected
            setSameTeamSelectionError(true);
            return;
        }
        else { // handle missing field errors
            homeTeam === "" ? setHomeTeamError(true) : setHomeTeamError(false);
            awayTeam === "" ? setAwayTeamError(true) : setAwayTeamError(false);
        }

        setSameTeamSelectionError(false);

        if (homeTeam !== "" && awayTeam !== "") {
            setIsSubmitted(true)
        }
    }

    return (
        <main className="page-body">
            <div className="instructions">
                <h1>Select Teams to Predict the Outcome</h1>
                <em>Choose a home team and an away team to make a prediction</em>
            </div>
            <Card display="flex-row">
                <form action="post" id='dashboard-form'>
                    <TeamSelectionForm
                        teamData={teamData}
                        homeTeam={homeTeam}
                        setHomeTeam={setHomeTeam}
                        awayTeam={awayTeam}
                        setAwayTeam={setAwayTeam}
                        homeTeamError={homeTeamError}
                        setHomeTeamError={setHomeTeamError}
                        awayTeamError={awayTeamError}
                        setAwayTeamError={setAwayTeamError}
                        sameTeamSelectionError={sameTeamSelectionError}
                    />
                    <div className="prediction-btn-container">
                        <button type="button" className="prediction-button" onClick={() => checkForTeamSelections()}>
                            Generate Prediction
                        </button>
                    </div>
                </form>
            </Card>
            <PredictionResults 
                prediction={prediction}
                error={error}
                loading={loading}
                isSubmitted={isSubmitted}
                teamData={teamData}
            />
        </main>
    )
}