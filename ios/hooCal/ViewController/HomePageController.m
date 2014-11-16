//
//  HomePageController.m
//  hooCal
//
//  Created by zhongtoby on 14/11/16.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "HomePageController.h"
#import <RLMRealm.h>
#import "UserInfo.h"
#import <RLMResults.h>

@implementation HomePageController
- (void)viewDidLoad {
    [super viewDidLoad];
    RLMResults *result = [UserInfo allObjects];
    if ([result firstObject]) {
        [self performSegueWithIdentifier:@"eventlist" sender:self];
    }
}
@end
