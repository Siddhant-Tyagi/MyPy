class groups:
    def __init__(self):
        self.counters_dict = {

                     'general_info': {
                                      'available': 'No',       
                                      'version': 'n/a',
                                      'running_for': 'n/a',
                                      'default_storage_engine': 'n/a',
                                      'innodb_version': 'n/a',
                                      'performance_schema': 'n/a',
                                      'uptime_since_flush_status': 'n/a', 
                                    },

                     'connection_history': {
                                            'attempts': 'n/a',
                                            'successful': 'n/a',
                                            'percentage_of_max_allowed_reached': 'n/a',
                                            'refused': 'n/a',
                                            'percentage_of_refused_connections': 'n/a',
                                            'terminated_abruptly': 'n/a',
                                            'bytes_received': 'n/a',
                                            'bytes_sent': 'n/a',
                                           },
                     
                     'current_connections': {
                                              'max_allowed': 'n/a',
                                              'open_connections': 'n/a',
                                              'connection_usage': 'n/a',
                                              'running_threads': 'n/a',
                                              'concurrent_connections': 'n/a',
                                              'idle_timeout': 'n/a',
                                              'max_interrupts': 'n/a',
                                              'connect_timeout': 'n/a',
                                              'back_log': 'n/a',
                                            },

                    }
