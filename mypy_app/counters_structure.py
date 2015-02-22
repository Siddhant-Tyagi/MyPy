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

                     'innodb_cache'  : {
                                         'innodb_buffer': 'n/a',
                                         'innodb_instances': 'n/a',
                                         'free_memory': 'n/a',
                                         'cache_blocks': 'n/a',
                                         'cache_misses': 'n/a',
                                         'cache_hit_ratio': 'n/a',
                                         'cache_write_wait': 'n/a',
                                         'adtl_pool_size': 'n/a',
                                         'free_page_waits': 'n/a',
                                         'buffer_max_size': 'n/a',
                                       },

                     'threads':      {
                                      'thread_cache_size': 'n/a',
                                      'threads_cached': 'n/a',
                                      'threads_created': 'n/a',
                                      'cache_hit_rate': 'n/a',
                                      'slow_launch_time': 'n/a',
                                      'slow_launch_threads': 'n/a',
                                     },
                     
                     'query_cache':  {
                                      'enabled': 'n/a',
                                      'type': 'n/a',
                                      'cache_size': 'n/a',
                                      'max_size': 'n/a',
                                      'free_memory': 'n/a',
                                      'query_buffer': 'n/a',
                                      'block_size': 'n/a',
                                      'total_blocks': 'n/a',
                                      'free_blocks': 'n/a',
                                      'fragmentation': 'n/a',
                                      'query_cache': 'n/a',
                                      'query_not_cached': 'n/a',
                                      'cache_misses': 'n/a',
                                      'cache_hits': 'n/a',
                                      'cache_hit_ratio': 'n/a',
                                      'queries_pruned': 'n/a',
                                      'pruned_percentage': 'n/a',
                                     },

                     'index_usage':  {
                                      'full_table_scans': 'n/a',
                                      'buffer': 'n/a',
                                      'select_scans': 'n/a',
                                      'buffer_joins': 'n/a',
                                      'joins_required': 'n/a',
                                      'joins_revaluate': 'n/a',
                                     },

                     'statements': {
                                    'all': 'n/a',
                                    'selects': 'n/a',
                                    'inserts': 'n/a',
                                    'updates': 'n/a',
                                    'deletes': 'n/a',
                                    'dms': 'n/a',
                                    'rows': 'n/a',
                                    'rows_index': 'n/a',
                                    'avg_rows': 'n/a',
                                    'rows_percentage': 'n/a',
                                    'max_prepared': 'n/a',
                                   },
                              
                     'replication': {
                                     'running': 'Not a slave',
                                     'read_only': 'n/a',
                                     'io_running': 'n/a',
                                     'io_state': 'n/a',
                                     'slave_sql': 'n/a',
                                     'sbm': 'n/a',
                                     'skip': 'n/a',
                                     'err_no': 'n/a',
                                     'err_msg': 'n/a',
                                     'io_err': 'n/a',
                                     'ntw_timeout': 'n/a',
                                     'trsc_count': 'n/a',
                                     'm_host': 'n/a',
                                     'm_port': 'n/a',
                                     'm_user': 'n/a',
                                     'mlog_file':  'n/a',
                                     'mlog_read_pos': 'n/a',
                                     'rm_log': 'n/a',
                                     'rm_log_pos': 'n/a',
                                     'rlog': 'n/a',
                                     'rlog_pos': 'n/a',
                                     },

                    }