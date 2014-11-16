//
//  Event.h
//  hooCal
//
//  Created by zhongtoby on 14/11/16.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "RLMObject.h"

@interface Event : RLMObject
@property NSString *title;
@property NSString *content;
@property NSDate *start_time;
@property NSDate *end_time;
@end
