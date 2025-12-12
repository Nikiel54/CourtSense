import { Link } from "react-router";
import basketballIcon from "../assets/basketball.png";

export default function Navbar({ selectedPage, setSelectedPage }) {

    return (
        <nav id="navbar">
            <div className="pg-title">
                <div className="logo-img-container">
                    <img className="logo-img" src={basketballIcon} alt="Image of a basketball" width="1.3em" height="auto"/>
                </div>
                <strong>NBA Match Predictor</strong>
            </div>
            <div className="nav-links">
                <Link to='/'
                    className={selectedPage === "Dashboard" ? "is-active-page" : "not-active-page"}
                    onClick={() => setSelectedPage("Dashboard")}>Dashboard
                </Link>
                <Link to='/analytics'
                    className={selectedPage === "Analytics" ? "is-active-page" : "not-active-page"}
                    onClick={() => setSelectedPage("Analytics")}>Team Analytics
                </Link>
                <Link to='/about'
                    className={selectedPage === "About" ? "is-active-page" : "not-active-page"}
                    onClick={() => setSelectedPage("About")}>About
                </Link>
            </div>
        </nav>
    )
}