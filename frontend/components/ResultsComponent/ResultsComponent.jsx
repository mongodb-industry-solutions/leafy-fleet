"use client"

import Card from '@leafygreen-ui/card';
import { H2, H3 } from '@leafygreen-ui/typography';


import Button, { Variant, Size } from '@leafygreen-ui/button';
import Icon from '@leafygreen-ui/icon';
import React from 'react';
const cars = [
  {
    id: "FL001",
    name: "Ford Transit",
    fleet: "Delivery Fleet",
    status: "active",
    location: "Downtown",
    driver: "John Doe",
    fuel: 85,
    mileage: 45230,
    lastService: "2024-01-15",
    efficiency: 18.5,
    alerts: 0,
    coordinates: [-74.006, 40.7128],
    zone: "Zone A - Downtown",
    distance: 0.5, // km from search point
  },
  {
    id: "FL002",
    name: "Mercedes Sprinter",
    fleet: "Delivery Fleet",
    status: "maintenance",
    location: "Garage A",
    driver: "Unassigned",
    fuel: 20,
    mileage: 67890,
    lastService: "2024-01-10",
    efficiency: 16.2,
    alerts: 2,
    coordinates: [-74.01, 40.72],
    zone: "Zone B - Industrial",
    distance: 1.2,
  },
  {
    id: "EX001",
    name: "BMW 7 Series",
    fleet: "Executive Fleet",
    status: "active",
    location: "Airport",
    driver: "Mike Johnson",
    fuel: 65,
    mileage: 23450,
    lastService: "2024-01-20",
    efficiency: 22.1,
    alerts: 0,
    coordinates: [-73.7781, 40.6413],
    zone: "Zone C - Airport",
    distance: 15.3,
  },
  {
    id: "EX002",
    name: "Audi A8",
    fleet: "Executive Fleet",
    status: "active",
    location: "City Center",
    driver: "Sarah Wilson",
    fuel: 90,
    mileage: 18900,
    lastService: "2024-01-18",
    efficiency: 21.8,
    alerts: 0,
    coordinates: [-74.0059, 40.7589],
    zone: "Zone A - Downtown",
    distance: 2.1,
  },
  {
    id: "SV001",
    name: "Chevrolet Silverado",
    fleet: "Service Fleet",
    status: "issue",
    location: "Route 45",
    driver: "Tom Brown",
    fuel: 40,
    mileage: 89200,
    lastService: "2023-12-28",
    efficiency: 14.3,
    alerts: 3,
    coordinates: [-74.1776, 40.7282],
    zone: "Crossing: Zone B → Zone D",
    distance: null,
    crossing: { from: "Zone B - Industrial", to: "Zone D - Warehouse" },
  },
  {
    id: "SV002",
    name: "Ford F-150",
    fleet: "Service Fleet",
    status: "active",
    location: "Warehouse B",
    driver: "Lisa Davis",
    fuel: 75,
    mileage: 56780,
    lastService: "2024-01-12",
    efficiency: 15.8,
    alerts: 1,
    coordinates: [-74.209, 40.7505],
    zone: "Zone D - Warehouse",
    distance: 8.7,
  },
]


const ResultsComponent = ( ) => {
      const getStatusIcon = (status) => {
    switch (status) {
      case "active":
        return <div className="w-2 h-2 bg-green-500 rounded-full"></div>
      case "maintenance":
        return <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
      case "issue":
        return <div className="w-2 h-2 bg-red-500 rounded-full"></div>
      default:
        return <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
    }
  }

  const handleCarClick = (car) => {
    setSelectedCar(car)
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setSelectedCar(null)
  }
    const [selectedCar, setSelectedCar] = React.useState(null);
  return (
    <Card className="p-0">
                  <div className="space-y-0">
                    {cars.map((car, index) => (
                      <div key={car.id}>
                        <div className="p-4 hover:bg-gray-50 transition-colors">
                          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 items-center">
                            <div>
                              <div className="flex items-center space-x-2">
                                {getStatusIcon(car.status)}
                                <span className="font-semibold">{car.id}</span>
                              </div>
                            </div>

                            <div>
                              <p className="text-sm font-medium">{car.driver}</p>
                              <p className="text-xs text-gray-500">{car.fleet}</p>
                            </div>

                            <div>
                              <p className="text-sm font-medium">{car.zone}</p>
                              {car.crossing && (
                                <p className="text-xs text-orange-600">
                                  Crossing: {car.crossing.from} → {car.crossing.to}
                                </p>
                              )}
                            </div>

                            {car.distance !== null && (
                              <div className="text-center">
                                <p className="text-sm font-medium">{car.distance} km</p>
                                <p className="text-xs text-gray-500">Distance</p>
                              </div>
                            )}

                            <div className="flex justify-end">
                              <Button size="sm" variant="outline" onClick={() => handleCarClick(car)}>
                                View Details
                              </Button>
                            </div>
                          </div>
                        </div>
                        {index < cars.length - 1 }
                      </div>
                    ))}
                  </div>
    </Card>
  );
}
export default ResultsComponent;