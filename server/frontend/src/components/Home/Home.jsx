import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import '../Dealers/Dealers.css';

function Home() {
  const [dealers, setDealers] = useState([]);
  const [filteredDealers, setFilteredDealers] = useState([]);
  const [states, setStates] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDealers();
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const response = await axios.get('/api/user/');
      if (response.data.authenticated) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.error('Error checking user:', error);
    }
  };

  const fetchDealers = async () => {
    try {
      const response = await axios.get('/api/dealers/');
      setDealers(response.data);
      setFilteredDealers(response.data);
      
      // Extract unique states
      const uniqueStates = [...new Set(response.data.map(dealer => dealer.state))];
      setStates(uniqueStates.sort());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dealers:', error);
      setLoading(false);
    }
  };

  const handleStateFilter = async (state) => {
    setSelectedState(state);
    if (state === '') {
      setFilteredDealers(dealers);
    } else {
      try {
        const response = await axios.get(`/api/dealers/state/${state}/`);
        setFilteredDealers(response.data);
      } catch (error) {
        console.error('Error filtering dealers:', error);
      }
    }
  };

  return (
    <div className="container mt-5">
      <div className="text-center mb-5">
        <h1 className="display-4 text-white fw-bold">Welcome to Car Dealership Portal</h1>
        <p className="lead text-white">
          Find the best car dealers across the nation. Read reviews and make informed decisions.
        </p>
      </div>

      <div className="card mb-4">
        <div className="card-body">
          <div className="row align-items-center">
            <div className="col-md-6">
              <h5>Filter by State</h5>
            </div>
            <div className="col-md-6">
              <select
                className="form-select"
                value={selectedState}
                onChange={(e) => handleStateFilter(e.target.value)}
              >
                <option value="">All States</option>
                {states.map((state, index) => (
                  <option key={index} value={state}>
                    {state}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center">
          <div className="spinner-border text-light" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : (
        <div className="row">
          {filteredDealers.length === 0 ? (
            <div className="col-12">
              <div className="alert alert-info">No dealers found.</div>
            </div>
          ) : (
            filteredDealers.map((dealer) => (
              <div key={dealer.id} className="col-md-4 mb-4">
                <div className="card h-100">
                  <div className="card-body">
                    <h5 className="card-title">{dealer.name}</h5>
                    <p className="card-text">
                      <strong>Location:</strong> {dealer.city}, {dealer.state}
                    </p>
                    <p className="card-text">
                      <strong>Phone:</strong> {dealer.phone}
                    </p>
                    <p className="card-text text-muted">{dealer.short_desc}</p>
                    <p className="card-text">
                      <small className="text-muted">
                        {dealer.review_count} review{dealer.review_count !== 1 ? 's' : ''}
                      </small>
                    </p>
                    <Link to={`/dealer/${dealer.id}`} className="btn btn-primary">
                      View Details
                    </Link>
                    {user && (
                      <Link
                        to={`/postreview/${dealer.id}`}
                        className="btn btn-outline-primary ms-2"
                      >
                        Review Dealer
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default Home;
