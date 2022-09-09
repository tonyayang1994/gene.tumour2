require([
  'jquery',
  'datatables.net',
  'datatables.net-bs',
  'datatables.net-colreorder',
  'datatables.net-rowreorder',
  'datatables.net-fixedcolumns',
  'datatables.net-fixedheader',
  'datatables.net-select',
  'bootstrap-modal-js',
  'jquery.auto-grow-input',
  'jquery.popupforms'
], function($) {
$(document).ready(function(){
    var $datable_object = $('#tumour_datatable');

    if ($datable_object.length) {
        var $formSearchableText = $('#form-SearchableText');
        var $formSearchField = $('#form-SearchField');
        var $formSearchFieldTitle = $('#form-SearchFieldTitle');
        var $formSearchDate = $('#form-SearchDate');
        var $formSearchDateTitle = $('#form-SearchDateTitle');
        var $formDateFrom = $('#form-date-from');
        var $formDateTo = $('#form-date-to');
        var $selectDropdown = $('#selectDropdown');
        var $form_searchbox = $('#form-searchbox');
        var table_height = $(window).innerHeight() -
            $datable_object.find('thead').height() -
            $datable_object.find('tfood').height() -
            $form_searchbox.closest('div.row').height() -
            $selectDropdown.closest('div.row').height() -
            35 /* id=data_table_paginate - */
            /* 25 id=data_table_length - */
             /* 21.row margin & padding */;
        var current_url = $('#ajax-target').attr('data-ajax-url');
        var data_url = current_url + '/@@genetumour-search-data';
        var _authenticator = $form_searchbox.find('input[name="_authenticator"]').val();
        // var columns_visible = $("body.userrole-manager, body.userrole-reviewer").length;
        var screen_width = window.screen.width;
        var leftColumns = 11;
        if ( screen_width < 768 ) {
            leftColumns = 0;
        }

        var $data_table = $datable_object.DataTable({
            scrollY: table_height,
            scrollX: true,
            scrollCollapse: true,
            autoWidth: true,
            searching: true,
            ordering: true,
            order: [[60, "desc"]],
            info: true,
            oLanguage: {"sUrl": "@@collective.js.datatables.translation"},
            // deferRender: [ 20, 1000 ],
            paging: true,
            lengthMenu: [10, 20, 50, 100, 200, 500],
            pageLength: 50,
            processing: true,
            serverSide: true,
            stateSave: true,
            stateDuration: -1,
            // rowId: 'DT_RowId',
            fixedColumns: {
                leftColumns: leftColumns,
                rightColumns: 0
            },
            select: {
                style:    'multi',
                selector: 'td:first-child'
            },
            columnDefs: [
                {
                    orderable: false,
                    searchable: false,
                    targets:   '_all'
                }/*,
                {
                    visible: columns_visible,
                    targets: [ 7, 8, 9, 10, 11, 12 ]
                }*/
            ],
            columns: [
                {
                    data: "url",
                    className: 'select-checkbox',
                    render: function (data, type, full, meta) {
                        //return '<input type="checkbox" name="paths:list" value = "' + data + '"/>';
                        // return '<input type="checkbox"/>';
                        return '';
                    }

                },
                {
                    data: null, defaultContent: '',
                    render: function (data, type, full, meta) {
                        var gid = full['DT_RowData']['gid'];
                        var indicator = [];
                        // length=32; Math.floor(32 / 6)=5
                        for (var i = 0; i < 2; i++) {
                            gid.slice(i * 6, (i + 1) * 6);
                            indicator.push('<div class="gid_box" style="background-color: #'
                                + gid.slice(i * 6, (i + 1) * 6) + '"></div>');
                        }
                        return indicator.join('');
                    }
                },

                {data: "steps", orderable: true, searchable: true},
                {data: "review_state", orderable: true, searchable: true},

                {data: "sample_no", orderable: true, searchable: true},
                {data: "barcode", orderable: true, searchable: true},
                {data: "name", orderable: true, searchable: true},

                {data: "result"},
                {
                    data: "result_info",
                    "render": function (data, type, full, meta) {
                        var result_info = '';
                        if (typeof data === "string" && data.length > 6) {
                            result_info = '<span data-toggle="tooltip" data-placement="right" ' +
                              'title="' + data + '">' + data.slice(0,8) + '...'  +'</span>';
                        }
                        else {
                            result_info =  data;
                        }
                        return result_info;
                    }
                },
                {
                    data: "quality_file",
                    "render": function (data, type, full, meta) {
                        var action = [];
                        if (data[0]) {
                            action.push('<a class="_FileDisplay" target="_blank" ' +
                              'href="' + data[0] + '">查看</a>');
                        }
                        if (data[1]) {
                            action.push('<a class="_FileDownload" ' +
                              'href="' + data[1] + '">下载</a>');
                        }
                        return action.join('/');
                    }
                },
                {
                    data: "result_file",
                    "render": function (data, type, full, meta) {
                        var action = [];
                        if (data[0]) {
                            action.push('<a class="_FileDisplay" target="_blank" ' +
                                'href="' + data[0] + '">查看</a>');
                        }
                        if (data[1]) {
                            action.push('<a class="_FileDownload" ' +
                                'href="' + data[1] + '">下载</a>');
                        }
                        return action.join('/');
                    }
                },

                {data: "sex"},
                {data: "age", orderable: true, searchable: true},
                {data: "inspection_item"},
                {data: "inspection_method"},
                {data: "submission_hospital"},
                {data: "submission_department"},
                {data: "submission_doctor"},
                {data: "pathological_diagnosis"},
                {data: "pathological_no"},
                {data: "treatment_situation"},
                {data: "received_operator"},
                {data: "received_phone"},
                {data: "received_address"},
                {data: "sample_type"},
                {data: "sampling_time"},
                {data: "received_time"},
                {data: "sample_size"},
                {data: "sample_note"},
                {data: "sample_source"},
                {data: "tcc_tcp"},

                {data: "task_no"},
                {data: "separation_time", orderable: true, searchable: true},
                {data: "separation_operator"},
                {data: "plasma_location"},
                {data: "separation_note"},
                {data: "extraction_time", orderable: true, searchable: true},
                {data: "na_extraction_type"},
                {data: "na_plasma_volume"},
                {data: "na_concentration", orderable: true, searchable: true},
                {data: "absorbance"},
                {data: "na_kit_no"},
                {data: "na_operator"},

                {data: "library_time", orderable: true, searchable: true},
                {data: "library_barcode"},
                {data: "library_concentration", orderable: true, searchable: true},
                {data: "library_operator"},
                {data: "library_kit_no"},
                {data: "library_location"},
                {data: "capture_concentration"},

                {data: "template_time", orderable: true, searchable: true},
                {data: "template_operator"},
                {data: "template_kit_no"},
                {data: "ot_instrument_no"},
                {data: "es_instrument_no"},
                {data: "sequencing_time", orderable: true, searchable: true},
                {data: "sequencing_operator"},
                {data: "sequencing_server"},
                {data: "sequencing_ip"},
                {data: "sequencing_filename"},

                {data: "created", orderable: true, searchable: true},
                {data: "modified", orderable: true, searchable: true},
                {
                    data: null, defaultContent: '',
                    "render": function (data, type, full, meta) {
                        var action = [];
                        if (data['can_changenote']) {
                            action.push('<a class="_ChangeNote pat-plone-modal" href="' +
                                data['url'] + '/@@genetumour-changenote">备注</a>');
                        }
                        if (data['can_versions']) {
                            action.push('<a class="_ContentHistory pat-plone-modal" href="' +
                                data['url'] + '/@@historyview">历史</a>');
                        }
                        return action.join(' ');
                    }
                }
            ],
            ajax: {
                url: data_url,
                type: "POST",
                data: function (dict) {
                    dict.search_field = $formSearchField.data('search_field');
                    dict.search_date = $formSearchDate.data('search_date');
                    dict.date_from = $formDateFrom.val();
                    dict.date_to = $formDateTo.val();
                    dict._authenticator = _authenticator;
                    //console.info(dict)
                    //dict.myKey = "myValue";
                    // etc
                }
            },
            initComplete: function (settings, json) {
            },
            rowCallback: function (row, data, index) {
            },
            drawCallback: function (settings) {
                // Row grouping
                var api = this.api();
                var rows = api.rows( {page:'current'} ).nodes();
                var last=null;

                // second draw
                /*if ($(rows).eq( 0 ).prev().length) {
                    return false;
                }
                api.column(1, {page:'current'} ).data().each( function ( row, i ) {
                    var group = row['DT_RowData']['gid'];
                    var row_td = new Array(64).join("<td></td>");
                    if ( last !== group ) {

                        $(rows).eq( i ).before(
                            // '<tr class="group"><td colspan="63">'+ ++i +'</td></tr>'
                            '<tr class="group">' + row_td + '</tr>'
                        );
                        last = group;
                    }
                });*/

                window.setTimeout(function () {
                    // Delay n millisecond waiting for draw finish.
                    $(window).scrollTop($form_searchbox.offset()['top'] - 2)
                }, 50)
            }
            /*stateSaveCallback: function(settings,data) {
                localStorage.setItem( 'DataTables_' + settings.sInstance, JSON.stringify(data) )
              },
            stateLoadCallback: function(settings) {
                return JSON.parse( localStorage.getItem( 'DataTables_' + settings.sInstance ) )
              },*/

        });


        $data_table.on(/*'order.dt search.dt'*/ 'draw.dt', function () {
            var info = $data_table.page.info();
            $data_table.column(1, {search: 'applied', order: 'applied'}).nodes().each(function (cell, i) {
                //cell.innerHTML = info.start + i + 1;
                var line_number = info.start + i + 1;
                var cell_content = cell.innerHTML;
                // Trigger two times
                if (!cell_content.endsWith(line_number)) {
                    cell.innerHTML = cell_content + (info.start + i + 1);
                }
            });
        });


        var columns_visible = $("body.userrole-manager, body.userrole-reviewer").length;
        $data_table.columns( [ 7, 8, 9, 10 ] ).visible( columns_visible, false );
        // $data_table.columns.adjust().draw( false ); // adjust column sizing and redraw


        /**
         * Fixed Columns
         * Responsive tables
         * Scroll horizontally on small devices (under 768px).
         */
        /*$(window).on('resize load',function(e){
            // table-responsive
            var screen_width = window.screen.width;
            var leftColumns = 11;

            if ( screen_width < 768 ) {
                leftColumns = 0;
            }
            var fc_object = new $.fn.dataTable.FixedColumns($data_table, {
                leftColumns: leftColumns,
                rightColumns: 1
            });
        });*/


        /**
         * ColReorder
         * click and drag any table header cell
         */
        // new $.fn.dataTable.ColReorder($data_table, {realtime: true});


        // Select by the grouping
        // $datable_object.find('tbody').on( 'click', 'tr.group', function () {
        //     console.log('click group title');
        // } );


        $datable_object.on( 'stateSaveParams.dt', function (e, settings, data) {
            data.date = {};
            data.date.start = $formDateFrom.val();
            data.date.end = $formDateTo.val();
            // data.search_field = {};
            // data.search_field.title = $formSearchFieldTitle.text();
            // data.search_field.value = $formSearchField.data('search_field');
            // data.search_date = {};
            // data.search_date.title = $formSearchDateTitle.text();
            // data.search_date.value = $formSearchDate.data('search_date');

        } );

        $datable_object.on( 'page.dt', function ( e, settings ) {
            var api = new $.fn.dataTable.Api( settings );
            api.state.save();
        } );

        $datable_object
            .on('init.dt', function ( e, settings ) {
                var api = new $.fn.dataTable.Api( settings );
                var state = api.state.loaded();
                // ... use `state` to restore information
                if(state){
                    $formSearchableText.val(state.search.search);
                    var page = parseInt( state.start / state.length );
                    $data_table.page( page );
                    if(state.date){
                         $formDateFrom.val(state.date.start);
                         $formDateTo.val(state.date.end);
                    }
                    // if(state.search_field){
                    //      $formSearchFieldTitle.text(state.search_field.title);
                    //      $formSearchField.data('search_field', state.search_field.value);
                    // if(state.search_date){
                    //      $formSearchDateTitle.text(state.search_date.title);
                    //      $formSearchDate.data('search_date', state.search_date.value);
                    // }
                }
            });


        $data_table.on( 'select.dt deselect.dt', function ( e, dt, type, indexes ) {
            var current_len = $data_table.page.info().end - $data_table.page.info().start;
            var selected_count = $data_table.rows( { selected: true } ).count();
            var $indicator = $selectDropdown.find(' span[data-target="indicator"]');

            if (current_len === selected_count && current_len > 0) {
                $indicator.prop('class', 'glyphicon glyphicon-check');
            }
            else if (current_len > selected_count && selected_count === 0) {
                $indicator.prop('class', 'glyphicon glyphicon-unchecked');
            }
            else if (current_len > selected_count) {
                $indicator.prop('class', 'glyphicon glyphicon-modal-window');
            }

            var $toggle_button = $(
                '#analysisBtnGroup a[data-target="step2-add"],' +
                '#analysisBtnGroup a[data-target="step3-add"],' +
                '#analysisBtnGroup a[data-target="step4-add"],' +
                '#analysisBtnGroup a[data-target="step5-add"],' +
                '#analysisBtnGroup a[data-target="step1-edit"],' +
                '#analysisBtnGroup a[data-target="step2-edit"],' +
                '#analysisBtnGroup a[data-target="step3-edit"],' +
                '#analysisBtnGroup a[data-target="step4-edit"],' +
                '#analysisBtnGroup a[data-target="step5-edit"],' +
                '#dataBtnGroup a[data-target="steps"], ' +
                '#dataBtnGroup a[data-target="state"], ' +
                '#dataBtnGroup a[data-target="redo"], ' +
                '#dataBtnGroup a[data-target="report"], ' +
                '#moreBtnGroup a[data-target="delete"], ' +
                '#moreBtnGroup a[data-target="export-item"], ' +
                '#moreBtnGroup a[data-target="export-dilution"]');
            if (selected_count) {
                //$toggle_button.show();
                $toggle_button.parent().removeClass('disabled');
                //$toggle_button.css('pointer-events', 'auto');
            }
            else {
                //$toggle_button.hide()
                $toggle_button.parent().addClass('disabled');
                //$toggle_button.css('pointer-events', 'none');
            }
        });


        $selectDropdown.on('click', '*[data-target]', function (event) {
            //event.stopPropagation();
            event.preventDefault();
            //console.log($(this).data('target'), $(event), event.target, event.relatedTarget)
            var target_data = $(this).data('target');
            var target_list = [
              'step1', 'step2', 'step3', 'step4', 'step5',
              'private', 'pending', 'success', 'failed', 'abort'];

            if (target_data === 'indicator') {
                var css_class = $(this).prop('class');

                if (css_class === 'glyphicon glyphicon-unchecked') {
                    $data_table.rows().select();
                }
                else if (css_class === 'glyphicon glyphicon-check' ||
                    css_class === 'glyphicon glyphicon-modal-window') {
                    $data_table.rows().deselect();
                }
            }
            else if (target_data === 'all') {
                $data_table.rows().select();
            }
            else if (target_data === 'none') {
                $data_table.rows().deselect();
            }
            else if ($.inArray(target_data, target_list) > -1) {
              $data_table.rows().deselect();
              $data_table.rows( '.' + target_data ).select();
            }
        });


        $datable_object.on('draw.dt', function () {
            $datable_object.find('>tbody>tr>td>div.gid_box')
                .on('dblclick', null, function (event) {
                    // !!! Columns has cloned, so change evnent coming from
                    // Fixed Columns Or Data Datable !!!
                    // event.stopPropagation();

                    //var gid = $(this).closest('tr').data('gid');
                    //console.info( $(this).closest('tr').data('steps') );
                    // Select Row
                    /*if ($(this).prop("checked")) {
                     $(this).closest('tr').find('>td>input[type="checkbox"]:first-of-type');
                     }*/

                });
        });

        $('#analysisBtnGroup a[data-target],' +
            '#dataBtnGroup a[data-target],' +
            '#moreBtnGroup a[data-target]')
            .on('click confirm.toolbar', null, function (event) {
                //event.stopPropagation();
                event.preventDefault();
                //console.log($(this).data('target'), $(event), event.target);
                var target_data = $(this).data('target');
                var target_list = [
                    'step1-import', 'step2-import', 'step3-import', 'step4-import', 'step5-import',
                    'step1-add', 'step2-add', 'step3-add', 'step4-add', 'step5-add',
                    'step1-edit', 'step2-edit', 'step3-edit', 'step4-edit', 'step5-edit',
                    'steps', 'state','redo', /*'report',*/
                    'delete', 'export-item', 'export-dilution', 'backup', 'recovery', 'check'
                ];
                //var target_list_all = [/*'import',*/, 'export-all'];
                if ($.inArray(target_data, target_list) === -1) {
                    return 0;
                }

                var $selected_row = $data_table.rows( { selected: true } ).data();
                // var $selected_row = $data_table.rows( { selected: true } ).nodes();
                var uuid_list = [];
                $selected_row.each(function (element, index) {
                    uuid_list.push(element['DT_RowData']['uuid']);
                    // uuid_list.push($(element).data('uuid'));
                });
                var uuid_length = uuid_list.length;

                var view = '.';
                var extraParameters = {};

                switch (target_data) {

                    case 'step1-import':
                        view = 'genetumour-import-excel';
                        extraParameters = {
                            'form.widgets.step': 'step1',
                            "form.buttons.submit": true
                        };
                        break;
                    case 'step2-import':
                        view = 'genetumour-import-excel';
                        extraParameters = {
                            'form.widgets.step': 'step2',
                            "form.buttons.submit": true
                        };
                        break;
                    case 'step3-import':
                        view = 'genetumour-import-excel';
                        extraParameters = {
                            'form.widgets.step': 'step3',
                            "form.buttons.submit": true
                        };
                        break;
                    case 'step4-import':
                        view = 'genetumour-import-excel';
                        extraParameters = {
                            'form.widgets.step': 'step4',
                            "form.buttons.submit": true
                        };
                        break;
                    case 'step5-import':
                        view = 'genetumour-import-excel';
                        extraParameters = {
                            'form.widgets.step': 'step5',
                            "form.buttons.submit": true
                        };
                        break;

                    case 'step1-add':
                        view = 'genetumour-blood-sample-addform';
                        break;
                    case 'step2-add':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-na-extraction-form';
                        break;
                    case 'step3-add':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-library-construction-form';
                        break;
                    case 'step4-add':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-computer-detecting-form';
                        break;
                    case 'step5-add':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-analysis-results-form';
                        break;

                    case 'step1-edit':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-blood-sample-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;
                    case 'step2-edit':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-na-extraction-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;
                    case 'step3-edit':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-library-construction-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;
                    case 'step4-edit':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-computer-detecting-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;
                    case 'step5-edit':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-analysis-results-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;

                    case 'redo':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-failed-redo-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;

                    case 'steps':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-change-steps-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;
                    case 'state':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-workflow-state-transition-form';
                        extraParameters = {
                            'form.widgets.edit': true
                        };
                        break;

                    case 'delete':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        // dismiss default click, waiting dialog confirm click.toolbar event.
                        if (event.type === 'click') {
                            var modal = $('#delete_modal_dialog').modal();
                            modal.find('.modal-body strong').text(uuid_length);
                            return 2;
                        }
                        view = 'genetumour-search-view';
                        break;

                    case 'export-item':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        view = 'genetumour-export-items';
                        break;
                    case 'export-dilution':
                        if (uuid_length === 0) {
                            return 0;
                        }
                        // var $btn_confirm = $('#dilution_modal_dialog')
                        //   .find('.modal-footer button[data-target="export-dilution"]');
                        // dismiss default click, waiting dialog confirm click.toolbar event.
                        if (event.type === 'click') {
                            // $btn_confirm.addClass('disabled').prop('disabled', true);

                            var bar_list=[];
                            $selected_row.each(function (element, index) {
                                bar_list.push(element['library_barcode']);
                                // bar_list.push($(element).data('library_barcode'));
                            });

                            var key_list=[];
                            var value_list=[];
                            var dict_list=[];
                            var i, j;

                            for (i=0, j=1; i<bar_list.length; i++, j++) {
                                var value = bar_list[i];
                                // if (bar_list.indexOf(value, j) > -1 && key_list.indexOf(value) === -1)
                                // {
                                //     key_list.push(value);
                                // }
                                if (bar_list.indexOf(value, j) > -1) {
                                    var name_index = key_list.indexOf(value);
                                    if (name_index === -1) {
                                        key_list.push(value);
                                        value_list[value_list.length] = 2;
                                    }
                                    else {
                                        value_list[name_index] += 1;
                                    }
                                }
                            }

                            for (i=0; i<key_list.length; i++) {
                                dict_list.push("'" + key_list[i] + "'" + ':' + value_list[i]);
                            }
                            var modal = $('#dilution_modal_dialog').modal();
                            modal.find('.modal-body strong._total').text(uuid_length);
                            modal.find('.modal-body strong._same').text(key_list.length);
                            modal.find('.modal-body span._bar').text(dict_list.join(', '));
                            // modal.find('.modal-body span._bar').text(key_list.sort().toString());
                            // $btn_confirm.removeClass('disabled').prop('disabled', false);

                            return 'Request confirmation';
                        }
                        view = 'genetumour-export-dilution';
                        break;
                    case 'backup':
                        view = 'genetumour-backup-view';
                        break;
                    case 'recovery':
                        view = 'genetumour-recovery-view';
                        break;
                    case 'check':
                        view = 'genetumour-check-error';
                        break;
                    default:
                        view = '.';
                        break;
                }

                var data = {uuids: uuid_list, bulk_action: target_data,
                  _authenticator: _authenticator/*, ajax_load: false*/};
                $.extend(data, extraParameters);
                var current_url = $('#ajax-target').attr('data-ajax-url');
                var post_url = current_url + '/@@'  +  view;
                submitForm(post_url, data);

                /*$.post(".", data, dataType = "html")
                 .done(function (data) {
                 console.log(data);
                 });*/
                //var href = window.location.pathname + '/' + view +'?' + $.param(data);
                //window.location.href = href;
            });


        var $delete_dialog = $('#delete_modal_dialog');
        $delete_dialog.find('.modal-footer button[data-target="delete"]')
            .on('click', function () {
                var target = $(this).data('target');
                $('#moreBtnGroup').find('a[data-target="' + target + '"]').triggerHandler('confirm.toolbar');
                $delete_dialog.modal('hide');
            });

         /**
         * Export dilution confirm mode dialog
         */
        var $dilution_dialog = $('#dilution_modal_dialog');
        $dilution_dialog.find('.modal-footer button[data-target="export-dilution"]')
            .on('click', function () {
                var target = $(this).data('target');
                $('#moreBtnGroup').find('a[data-target="' + target + '"]').triggerHandler('confirm.toolbar');
                $dilution_dialog.modal('hide');
            });


        $formSearchableText
            .on('keypress', function (event) {
                if (event.keyCode == 13) {
                    $data_table.search(this.value).draw();
                }
            });
/* cancel popover by adam
        $("#form-SearchableHelp")
            .popover({
                html: true,
                content: $('#tooltip-SearchableText').html(),
                template: '<div class="popover" role="tooltip" style="max-width: inherit; ">' +
                '<div class="arrow"></div>' +
                '<h3 class="popover-title"></h3>' +
                '<div class="popover-content"></div></div>',
                placement: 'auto rigth'
                //viewport: '#form-SearchableText'
            });
            */
        /*.on('shown.bs.popover', function () {
         $('#' + this.getAttribute('aria-describedby'))
         .insertAfter($(this)
         .parent().parent());
         });*/

        $("#form-SearchableClear, #form-date-from-clear, #form-date-to-clear")
            .on('click', function (event) {
                var target = $(this).data('for');
                var $target_input = $('#' + target);
                if ($target_input.val() === '')
                {
                  return
                }
                $target_input.val('');

                var clear_id = $(this).prop('id');

                if ((clear_id == 'form-date-from-clear' ||
                    clear_id == 'form-date-to-clear') && !$formSearchDate.data('search_date')) {
                    return
                }
                // Create a new jQuery.Event object with specified event properties.
                var event = jQuery.Event( "keypress", { keyCode: 13 } );
                // trigger an artificial keydown event with keyCode 13
                $formSearchableText.triggerHandler( event );
            });

        $formSearchField
            .on('click', '*[data-target]', function (event) {
                //event.stopPropagation();
                event.preventDefault();
                //console.log(this, event);
                //console.info(event.target, event.currentTarget, event.delegateTarget, event.relatedTarget);
                var $clicked_btn = $(this);

                if ($formSearchFieldTitle.text() === $clicked_btn.text()) {
                    return 0;
                }
                else {
                    $formSearchFieldTitle.text($clicked_btn.text());
                }

                $formSearchField.data('search_field', $clicked_btn.data('target'));
                var key_event = jQuery.Event('keypress', {keyCode: 13});
                $formSearchableText.triggerHandler(key_event);
            });

        $formSearchDate
            .on('click', '*[data-target]', function (event) {
                //event.stopPropagation();
                event.preventDefault();
                //console.log(this, event);
                //console.info(event.target, event.currentTarget, event.delegateTarget, event.relatedTarget);
                var $clicked_btn = $(this);

                if ($formSearchDateTitle.text() === $clicked_btn.text()) {
                    return 0;
                }
                else {
                    $formSearchDateTitle.text($clicked_btn.text());
                }

                $formSearchDate.data('search_date', $clicked_btn.data('target'));
                if ($formSearchDate.data('search_date') &&
                    !($formDateFrom.val() || $formDateTo.val())) {
                  return
                }
                var key_event = jQuery.Event('keypress', {keyCode: 13});
                $formSearchableText.triggerHandler(key_event);
            });


        $datable_object
            .on('draw.dt', function () {
                $('span[data-toggle="tooltip"]').tooltip();
            });


        $datable_object
            .on('init.dt', function () {
                $('#datatable_info')
                  .append($('#tumour_datatable_length').css('display', 'inline'))
                  .append($('#tumour_datatable_info').css('display', 'inline'));
                $('#datatable_paginate').append($('#tumour_datatable_paginate'));
            });

        ( function( $ ) {
            $datable_object
                .on( 'processing.dt', function ( e, settings, processing ) {
                    count = $data_table.page.len();
                    total_seconds = Math.round( count * speed );
                    progressbar.progressbar( "option", "max", total_seconds );

                    $('#progress-container').css( 'display', processing ? 'block' : 'none' );

                    if (processing && progressTimer==null) {
                        progressTimer = setTimeout(progress, 0);
                    }
                    else if ( !processing ) {
                        clearTimeout(progressTimer);
                        progressTimer = null;
                        progressbar.progressbar("value", 0);
                        progressLabel.text("");
                    }
                } );

            var count = $data_table.page.len(),
                speed = 0.006,
                total_seconds = Math.round( count * speed ),
                progressTimer = null,
                progressLabel = $(".progress-label"),
                progressbar = $("#progressbar");

            progressbar.progressbar({
                value: 0,
                max: total_seconds,
                change: function () {
                    var val = progressbar.progressbar("value");
                    var percent = Math.round( ( (val / total_seconds).toFixed(2) - 0 ) * 100);
                    if (val){
                        progressLabel.text(percent + "%");
                    }
                },
                complete: function () {
                    progressLabel.text("");
                    progressbar.progressbar( "value", false );
                }
            });

            function progress() {
                var val = progressbar.progressbar("value") || 0;
                progressbar.progressbar("value", (val + 0.1).toFixed(1) - 0);
                if (val < total_seconds - 0.1) {
                    progressTimer = setTimeout(progress, 100);
                }
            }
        } )( jQuery );

    }


    ( function( $ ) {
        if ( $('#genetumour-import-form').length ) {

        var $form_file = $("#form-widgets-excelFile"),
            backcount = $form_file.data('backcount') - 0,
            filename = $form_file.data('filename'),
            simulation = $form_file.data('simulation'),
            steps = $('#form-widgets-step').val(),
            speed = 0.3;

        if (steps === 'step1') {
             speed = 0.3;
        }
        else if (steps === 'step2') {
             speed = 0.13;
        }
        else if (steps === 'step3') {
             speed = 0.18;
        }
        else if (steps === 'step4') {
             speed = 0.13;
        }
        else if (steps === 'step5') {
             speed = 1.0;
        }

        var total_seconds = Math.round( backcount * speed );
        var progressTimer,
            progressbar = $("#progressbar"),
            progressLabel = $(".progress-label"),
            importButton = $("#form-buttons-import")
                .on("click", function () {
                    var current_filename = $form_file.val().split("\\").pop(),
                        current_simulation = $("#form-widgets-simulation").prop("checked");
                    if ( !( !current_simulation &&
                        simulation != "" &&
                        current_filename != "" &&
                        current_filename == filename &&
                        backcount > 0 ) ) {
                        // return;
                        progressLabel.text("");
                        progressbar.progressbar( "value", false );
                    }
                    else {
                        progressTimer = setTimeout(progress, 1200);
                    }
                    // $(this).prop('disabled', true);
                    importButton
                        .addClass('disabled')
                        .css('pointer-events', 'none');
                    $("div.resultSteps").hide();
                    $( "#progress-container" ).show( "slide", 1000 );
                }),
            cancelButton = $("#form-buttons-cancel")
                .on("click", function () {
                    // $(this).prop('disabled', true);
                    importButton
                       .removeClass('disabled')
                       .css('pointer-events', 'auto');
                   cancelBackup();
                });

        progressbar.progressbar({
            value: 0,
            max: total_seconds,
            change: function () {
                var val = progressbar.progressbar("value");
                var percent = Math.round( ( (val / total_seconds).toFixed(2) - 0 ) * 100);
                if (val){
                    progressLabel.text(percent + "%");
                }
            },
            complete: function () {
                progressLabel.text("");
                progressbar.progressbar( "value", false );

            }
        });

        function progress() {
            var val = progressbar.progressbar("value") || 0;
            progressbar.progressbar("value", (val + 0.1).toFixed(1) - 0);
            if (val < total_seconds - 0.1) {
                progressTimer = setTimeout(progress, 100);
            }
        }

        function cancelBackup() {
            clearTimeout(progressTimer);
            progressbar.progressbar("value", 0);
            progressLabel.text("Loading...");
            $( "#progress-container" ).hide( "slide" );
        }
    }
    } )( jQuery );


    ( function( $ ) {
        if ( $('#genetumour-backup-form').length ) {

        var total_seconds = $("#estimated_backup_time").data('estimated_seconds') - 0;
        var progressTimer,
            progressbar = $("#progressbar"),
            progressLabel = $(".progress-label"),
            backupButton = $("#form-buttons-backup")
                .on("click", function () {
                    // $(this).prop('disabled', true);
                    backupButton
                        .addClass('disabled')
                        .css('pointer-events', 'none');
                    progressTimer = setTimeout(progress, 1200);
                    $( "#progress-container" ).show( "slide", 1000 );
                }),
            cancelButton = $("#form-buttons-cancel")
                .on("click", function () {
                    // $(this).prop('disabled', true);
                    backupButton
                       .removeClass('disabled')
                       .css('pointer-events', 'auto');
                    cancelBackup();
                });

        progressbar.progressbar({
            value: 0,
            max: total_seconds,
            change: function () {
                var val = progressbar.progressbar("value");
                var percent = Math.round( ( (val / total_seconds).toFixed(2) - 0 ) * 100);
                if (val){
                    progressLabel.text(percent + "%");
                }
            },
            complete: function () {
                progressLabel.text("");
                progressbar.progressbar( "value", false );

            }
        });

        function progress() {
            var val = progressbar.progressbar("value") || 0;
            progressbar.progressbar("value", (val + 0.1).toFixed(1) - 0);
            if (val < total_seconds - 0.1) {
                progressTimer = setTimeout(progress, 100);
            }
        }

        function cancelBackup() {
            clearTimeout(progressTimer);
            progressbar.progressbar("value", 0);
            progressLabel.text("Loading...");
            $( "#progress-container" ).hide( "slide" );
        }
    }
    } )( jQuery );


    ( function( $ ) {
        if ( $('#genetumour-check-error-form').length ) {

        var progressbar = $("#progressbar"),
            progressLabel = $(".progress-label"),
            backupButton = $("#form-buttons-check")
                .on("click", function () {
                    // cancelButton.prop('disabled', true);
                    $(this)
                        .addClass('disabled')
                        .css('pointer-events', 'none');
                    $( "#progress-container" ).show( "slide", 1000 );
                    $( "document" ).one( "ready", function() {
                        cancelCheck();
                    });
                }),
            cancelButton = $("#form-buttons-cancel")
                .on("click", function () {
                    //$(this).prop('disabled', true);
                    backupButton
                        .removeClass('disabled')
                        .css('pointer-events', 'auto');
                    cancelCheck();
                });

        progressbar.progressbar({
            value: false,
            max: 0,
            complete: function () {
                progressLabel.text("");
                progressbar.progressbar( "value", false );

            }
        });

        function cancelCheck() {
            progressbar.progressbar("value", false);
            // progressLabel.text("Loading...");
            $( "#progress-container" ).hide( "slide" );
        }
    }
    } )( jQuery );



    if ($('body.template-genetumour-controlpanel').length) {
        $('#form-widgets-sms_notify_message')
          .prevAll('label')
          .children('span.formHelp')
          .contents()
          .after(' ');
/*
        $('a#sms-help-info').prepOverlay({
              subtype: 'ajax',
              cssclass: 'overlay-sms-help',
              filter: '#content-core'
          });
*/

        $('select[id^=form-widgets-user_search_filter-key-]')
            .on('change', function () {
                var steps_color = '#' + stringToHex(this.value).slice(-7, -1);
                $(this).parent().css('border-left', '5px solid ' + steps_color);
            })
            .change();

    }

     var $batch_list = $('table[id^="form-tumour"]');
     $batch_list.find('span.namedblobfile-field input[value="replace"]').click();

    function submitForm(action, params) {
        $('#_submitForm').remove();
        var form = $('<form enctype="multipart/form-data" style="display: none;"></form>');
        form.prop('id', '_submitForm');
        form.prop('action', action);
        form.prop('method', 'post');
        form.prop('target', '_self');
        //for (var i = 0; i < params.length; i++) {
        //    var input1 = $('<input type="hidden" name="' + params[i].name + '" />');
        //    input1.prop('value', params[i].val);
        //    form.append(input1);
        //}
        $.each(params, function (key, value) {
            var input1 = $('<input type="hidden" name="' + key + '" />');
            input1.prop('value', value);
            form.append(input1);
        });
        form.appendTo('body');
        form.css('display', 'none');
        form.submit();
    }

    function stringToHex(str) {
        var val = '';
        for (var i = 0; i < str.length; i++) {
            val += str.charCodeAt(i).toString(16);
        }
        return val;
    }

});
});
