# Miscellaneous info required for running DeathStarBench scripting

# Directory paths are relative to grpc-hotel-ipu/scripts/
application_info = {
    #'HOTELRESERVATION_GRPC' : {
    #    'node_dir_path' : '/users/{0}/medium_hotel_db_replica_profile_mongo/DeathStarBench/hotelReservation',
    #    'wrk2_points_path' : '~/medium_hotel_db_replica_profile_mongo/DeathStarBench/hotelReservation/data/wrk2_points.txt',
    #    'workload_lua_path' : '../datacenter-soc/workload_generator/modified-mixed-workload.lua',
    #    'wrk_csrc_path' : '~/wrk2/src/wrk.c',
    #    'manager_dir_path' : '../datacenter-soc/modified_hotel_reservation_applications/medium_hotel_db_replica_profile_mongo/DeathStarBench/hotelReservation',
    #    'zip_paths' : {'app' : '../datacenter-soc/modified_hotel_reservation_applications/medium_hotel_db_replica_profile_mongo',
    #                   'wrk' : '../datacenter-soc/workload_generator/wrk2'}
    #},
    'SOCIALNETWORK' : {
        'manager_dsb_path' : '/dev/shm/hardware-systems-sustainability/DeathStarBench/socialNetwork',
        'worker_dsb_path'  : '/users/{0}/DeathStarBench/socialNetwork',
        'docker_name'      : 'socialNetwork'
    }
}
