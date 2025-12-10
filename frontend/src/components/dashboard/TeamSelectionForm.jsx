
export function TeamSelectionForm({
    team_data, 
    homeTeam, 
    setHomeTeam, 
    awayTeam, 
    setAwayTeam, 
    homeTeamError, 
    setHomeTeamError,
    awayTeamError,
    setAwayTeamError,
}) {
    return (
        <>
            <div>
                <label>
                    Home Team
                    <button type="button" className="selection-btn">
                        <select
                            name="Home Team"
                            value={homeTeam === "" ? "" : homeTeam.name}
                            onChange={(e) => {
                                if (e.target.value === "") {
                                    setHomeTeam("");
                                } else {
                                    setHomeTeam(team_data.find((team) => team.name === e.target.value));
                                    setHomeTeamError(false);
                                }
                            }}>
                            <option key="0" value="">Select a team</option>
                            {team_data.map((team) => {
                                return (
                                    <option key={team.id} value={team.name}>{team.name}</option>
                                )
                            })}
                        </select>
                    </button>
                </label>
                {homeTeamError &&
                    <strong className="error-txt">Missing Home Team!</strong>
                }
            </div>
            <div>
                <label>
                    Away Team
                    <button type="button" className="selection-btn">
                        <select
                            name="Away Team"
                            value={awayTeam === "" ? "" : awayTeam.name}
                            onChange={(e) => {
                                if (e.target.value === "") {
                                    setAwayTeam("");
                                } else {
                                    setAwayTeam(team_data.find((team) => team.name === e.target.value));
                                    setAwayTeamError(false);
                                }
                            }}>
                            <option key="0" value="">Select a team</option>
                            {team_data.map((team) => {
                                return (
                                    <option key={team.id} value={team.name}>{team.name}</option>
                                )
                            })}
                        </select>
                    </button>
                </label>
                {awayTeamError &&
                    <strong className="error-txt">Missing Away Team!</strong>
                }
            </div>
        </>
                    
    )
}