import Navbar from "./Navbar"
import Footer from "./Footer"
import { Outlet } from "react-router"
import { useState } from "react"

export default function Layout() {
    const [selectedPage, setSelectedPage] = useState("Dashboard")

    return (
        <>
            <Navbar selectedPage={selectedPage} setSelectedPage={setSelectedPage} />
            <Outlet />
            <Footer/>
        </>
    )
}